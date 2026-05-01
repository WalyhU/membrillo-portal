from decimal import Decimal
from typing import List, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from . import models, schemas
from .sse import broker

IVA_RATE = Decimal("0.12")


def listar_tipos(db: Session) -> List[models.TipoProducto]:
    return db.query(models.TipoProducto).all()


def listar_productos(db: Session) -> List[dict]:
    rows = (
        db.query(
            models.Producto,
            models.TipoProducto.nombre.label("tipo_nombre"),
            func.coalesce(func.sum(models.StockSucursal.existencia), 0).label("stock_total"),
        )
        .join(models.TipoProducto, models.Producto.tipo_id == models.TipoProducto.id)
        .outerjoin(models.StockSucursal, models.StockSucursal.producto_id == models.Producto.id)
        .filter(models.Producto.activo == 1)
        .group_by(models.Producto.id, models.TipoProducto.nombre)
        .order_by(models.Producto.id)
        .all()
    )
    out = []
    for prod, tipo_nombre, stock_total in rows:
        out.append({
            "id": prod.id,
            "nombre": prod.nombre,
            "descripcion": prod.descripcion,
            "precio": prod.precio,
            "imagen_url": prod.imagen_url,
            "tipo_nombre": tipo_nombre,
            "stock_total": int(stock_total or 0),
        })
    return out


def obtener_producto(db: Session, producto_id: int) -> models.Producto | None:
    return (
        db.query(models.Producto)
        .options(joinedload(models.Producto.tipo))
        .filter(models.Producto.id == producto_id, models.Producto.activo == 1)
        .first()
    )


def stock_por_sucursal(db: Session, producto_id: int) -> List[dict]:
    rows = (
        db.query(models.StockSucursal, models.Sucursal.nombre)
        .join(models.Sucursal, models.StockSucursal.sucursal_id == models.Sucursal.id)
        .filter(models.StockSucursal.producto_id == producto_id)
        .order_by(models.Sucursal.id)
        .all()
    )
    return [
        {"sucursal_id": s.sucursal_id, "sucursal_nombre": nombre, "existencia": s.existencia}
        for s, nombre in rows
    ]


def stock_total_producto(db: Session, producto_id: int) -> int:
    total = db.query(func.coalesce(func.sum(models.StockSucursal.existencia), 0)).filter(
        models.StockSucursal.producto_id == producto_id
    ).scalar()
    return int(total or 0)


def listar_sucursales(db: Session) -> List[models.Sucursal]:
    return db.query(models.Sucursal).order_by(models.Sucursal.id).all()


def encontrar_o_crear_cliente(db: Session, datos: schemas.CheckoutIn) -> models.Cliente:
    if datos.email:
        existente = db.query(models.Cliente).filter(models.Cliente.email == datos.email).first()
        if existente:
            return existente
    cli = models.Cliente(
        nombre=datos.nombre,
        nit=datos.nit or "CF",
        email=datos.email,
        telefono=datos.telefono,
        direccion=datos.direccion,
    )
    db.add(cli)
    db.flush()
    return cli


def reservar_stock(db: Session, sucursal_id: int, items: List[schemas.ItemCarrito]) -> List[Tuple[models.StockSucursal, int]]:
    """Bloquea filas con SELECT...FOR UPDATE y devuelve lista de (stock_row, cantidad)."""
    reservas = []
    for item in items:
        row = (
            db.query(models.StockSucursal)
            .filter(
                models.StockSucursal.producto_id == item.producto_id,
                models.StockSucursal.sucursal_id == sucursal_id,
            )
            .with_for_update()
            .first()
        )
        if row is None:
            raise ValueError(f"Producto {item.producto_id} no disponible en sucursal {sucursal_id}")
        if row.existencia < item.cantidad:
            raise ValueError(
                f"Stock insuficiente para producto {item.producto_id}: hay {row.existencia}, piden {item.cantidad}"
            )
        reservas.append((row, item.cantidad))
    return reservas


def crear_factura(db: Session, datos: schemas.CheckoutIn) -> models.Factura:
    cliente = encontrar_o_crear_cliente(db, datos)
    reservas = reservar_stock(db, datos.sucursal_id, datos.items)

    productos_map = {p.id: p for p in db.query(models.Producto).filter(
        models.Producto.id.in_([i.producto_id for i in datos.items])
    ).all()}

    subtotal = Decimal("0")
    detalles: List[models.DetalleFactura] = []
    for item in datos.items:
        prod = productos_map[item.producto_id]
        sub = (prod.precio * item.cantidad).quantize(Decimal("0.01"))
        detalles.append(models.DetalleFactura(
            producto_id=prod.id,
            cantidad=item.cantidad,
            precio_unit=prod.precio,
            subtotal=sub,
        ))
        subtotal += sub

    iva = (subtotal * IVA_RATE).quantize(Decimal("0.01"))
    total = (subtotal + iva).quantize(Decimal("0.01"))

    factura = models.Factura(
        cliente_id=cliente.id,
        sucursal_id=datos.sucursal_id,
        subtotal=subtotal,
        iva=iva,
        total=total,
        estado="pagada",
        detalles=detalles,
    )
    db.add(factura)

    eventos = []
    for stock_row, cantidad in reservas:
        stock_row.existencia -= cantidad
        eventos.append((stock_row.producto_id, stock_row.sucursal_id, stock_row.existencia))

    db.commit()
    db.refresh(factura)

    for prod_id, suc_id, exist in eventos:
        total_prod = stock_total_producto(db, prod_id)
        broker.publish({
            "producto_id": prod_id,
            "sucursal_id": suc_id,
            "existencia": exist,
            "stock_total": total_prod,
        })

    return factura


def ajustar_stock(db: Session, producto_id: int, sucursal_id: int, nueva_existencia: int) -> models.StockSucursal:
    row = db.query(models.StockSucursal).filter(
        models.StockSucursal.producto_id == producto_id,
        models.StockSucursal.sucursal_id == sucursal_id,
    ).with_for_update().first()
    if row is None:
        raise ValueError("Combinacion producto/sucursal no existe")
    row.existencia = max(0, int(nueva_existencia))
    db.commit()
    db.refresh(row)
    total_prod = stock_total_producto(db, producto_id)
    broker.publish({
        "producto_id": producto_id,
        "sucursal_id": sucursal_id,
        "existencia": row.existencia,
        "stock_total": total_prod,
    })
    return row


def obtener_factura(db: Session, factura_id: int) -> models.Factura | None:
    return (
        db.query(models.Factura)
        .options(
            joinedload(models.Factura.cliente),
            joinedload(models.Factura.sucursal),
            joinedload(models.Factura.detalles).joinedload(models.DetalleFactura.producto),
        )
        .filter(models.Factura.id == factura_id)
        .first()
    )
