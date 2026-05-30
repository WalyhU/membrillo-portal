from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from . import models, schemas
from .sse import broker

IVA_RATE = Decimal("0.12")
RESERVA_TTL_MIN = 15           # minutos que dura una reserva antes de liberarse
STOCK_BAJO_UMBRAL = 30         # disponible por debajo de esto = "stock bajo"


# ----------- Lecturas catalogo -----------

def listar_tipos(db: Session) -> List[models.TipoProducto]:
    return db.query(models.TipoProducto).all()


def listar_productos(db: Session) -> List[dict]:
    rows = (
        db.query(
            models.Producto,
            models.TipoProducto.nombre.label("tipo_nombre"),
            func.coalesce(func.sum(models.StockSucursal.existencia), 0).label("stock_total"),
            func.coalesce(func.sum(models.StockSucursal.reservado), 0).label("reservado_total"),
        )
        .join(models.TipoProducto, models.Producto.tipo_id == models.TipoProducto.id)
        .outerjoin(models.StockSucursal, models.StockSucursal.producto_id == models.Producto.id)
        .filter(models.Producto.activo == 1)
        .group_by(models.Producto.id, models.TipoProducto.nombre)
        .order_by(models.Producto.id)
        .all()
    )
    out = []
    for prod, tipo_nombre, stock_total, reservado_total in rows:
        stock_total = int(stock_total or 0)
        reservado_total = int(reservado_total or 0)
        out.append({
            "id": prod.id,
            "nombre": prod.nombre,
            "descripcion": prod.descripcion,
            "precio": prod.precio,
            "imagen_url": prod.imagen_url,
            "tipo_id": prod.tipo_id,
            "tipo_nombre": tipo_nombre,
            "stock_total": stock_total,
            "reservado_total": reservado_total,
            "disponible_total": max(0, stock_total - reservado_total),
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
        {
            "sucursal_id": s.sucursal_id,
            "sucursal_nombre": nombre,
            "existencia": s.existencia,
            "reservado": s.reservado,
            "disponible": s.disponible,
        }
        for s, nombre in rows
    ]


def stock_total_producto(db: Session, producto_id: int) -> int:
    total = db.query(func.coalesce(func.sum(models.StockSucursal.existencia), 0)).filter(
        models.StockSucursal.producto_id == producto_id
    ).scalar()
    return int(total or 0)


def listar_sucursales(db: Session) -> List[models.Sucursal]:
    return db.query(models.Sucursal).order_by(models.Sucursal.id).all()


# ----------- SSE helper -----------

def _publicar_stock(db: Session, producto_id: int, sucursal_id: int) -> None:
    """Lee el estado actual de una celda producto/sucursal y lo difunde por SSE."""
    row = db.query(models.StockSucursal).filter(
        models.StockSucursal.producto_id == producto_id,
        models.StockSucursal.sucursal_id == sucursal_id,
    ).first()
    existencia = row.existencia if row else 0
    reservado = row.reservado if row else 0

    sums = db.query(
        func.coalesce(func.sum(models.StockSucursal.existencia), 0),
        func.coalesce(func.sum(models.StockSucursal.reservado), 0),
    ).filter(models.StockSucursal.producto_id == producto_id).first()
    stock_total = int(sums[0] or 0)
    reservado_total = int(sums[1] or 0)

    broker.publish({
        "producto_id": producto_id,
        "sucursal_id": sucursal_id,
        "existencia": existencia,
        "reservado": reservado,
        "disponible": max(0, existencia - reservado),
        "stock_total": stock_total,
        "disponible_total": max(0, stock_total - reservado_total),
    })


# ----------- Clientes -----------

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


# ----------- Reservas de stock -----------

def reservar_stock(db: Session, factura_id: int, sucursal_id: int, items: List[schemas.ItemCarrito]) -> List[tuple]:
    """Bloquea filas con SELECT...FOR UPDATE, valida disponible (existencia - reservado),
    incrementa reservado y crea filas Reserva con TTL. NO toca existencia."""
    expira = datetime.utcnow() + timedelta(minutes=RESERVA_TTL_MIN)
    afectados = []
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
        disponible = row.existencia - row.reservado
        if disponible < item.cantidad:
            raise ValueError(
                f"Stock insuficiente para producto {item.producto_id}: disponibles {disponible}, piden {item.cantidad}"
            )
        row.reservado += item.cantidad
        db.add(models.Reserva(
            factura_id=factura_id,
            producto_id=item.producto_id,
            sucursal_id=sucursal_id,
            cantidad=item.cantidad,
            estado="activa",
            expira_en=expira,
        ))
        afectados.append((item.producto_id, sucursal_id))
    return afectados


def confirmar_reservas(db: Session, factura_id: int) -> None:
    """Pago aprobado: baja existencia, libera reservado, marca reservas confirmadas."""
    reservas = db.query(models.Reserva).filter(
        models.Reserva.factura_id == factura_id,
        models.Reserva.estado == "activa",
    ).all()
    afectados = set()
    for r in reservas:
        row = db.query(models.StockSucursal).filter(
            models.StockSucursal.producto_id == r.producto_id,
            models.StockSucursal.sucursal_id == r.sucursal_id,
        ).with_for_update().first()
        if row:
            row.existencia = max(0, row.existencia - r.cantidad)
            row.reservado = max(0, row.reservado - r.cantidad)
        r.estado = "confirmada"
        afectados.add((r.producto_id, r.sucursal_id))
    db.commit()
    for prod_id, suc_id in afectados:
        _publicar_stock(db, prod_id, suc_id)


def liberar_reservas(db: Session, factura_id: int) -> None:
    """Pago rechazado/cancelado: devuelve reservado, marca reservas liberadas."""
    reservas = db.query(models.Reserva).filter(
        models.Reserva.factura_id == factura_id,
        models.Reserva.estado == "activa",
    ).all()
    afectados = set()
    for r in reservas:
        row = db.query(models.StockSucursal).filter(
            models.StockSucursal.producto_id == r.producto_id,
            models.StockSucursal.sucursal_id == r.sucursal_id,
        ).with_for_update().first()
        if row:
            row.reservado = max(0, row.reservado - r.cantidad)
        r.estado = "liberada"
        afectados.add((r.producto_id, r.sucursal_id))
    db.commit()
    for prod_id, suc_id in afectados:
        _publicar_stock(db, prod_id, suc_id)


def liberar_reservas_vencidas(db: Session) -> int:
    """Libera reservas activas cuyo TTL expiro. Devuelve cuantas libero."""
    ahora = datetime.utcnow()
    vencidas = db.query(models.Reserva).filter(
        models.Reserva.estado == "activa",
        models.Reserva.expira_en < ahora,
    ).all()
    if not vencidas:
        return 0
    afectados = set()
    facturas = set()
    for r in vencidas:
        row = db.query(models.StockSucursal).filter(
            models.StockSucursal.producto_id == r.producto_id,
            models.StockSucursal.sucursal_id == r.sucursal_id,
        ).with_for_update().first()
        if row:
            row.reservado = max(0, row.reservado - r.cantidad)
        r.estado = "liberada"
        afectados.add((r.producto_id, r.sucursal_id))
        facturas.add(r.factura_id)
    # marca facturas pendientes asociadas como anuladas
    if facturas:
        db.query(models.Factura).filter(
            models.Factura.id.in_(facturas),
            models.Factura.estado == "pendiente",
        ).update({models.Factura.estado: "anulada"}, synchronize_session=False)
    db.commit()
    for prod_id, suc_id in afectados:
        _publicar_stock(db, prod_id, suc_id)
    return len(vencidas)


# ----------- Facturacion -----------

def crear_factura(db: Session, datos: schemas.CheckoutIn, cliente_id: Optional[int] = None) -> models.Factura:
    """Crea factura PENDIENTE y reserva stock. La existencia baja solo al confirmar el pago."""
    if cliente_id is None:
        cliente = encontrar_o_crear_cliente(db, datos)
        cliente_id = cliente.id

    productos_map = {p.id: p for p in db.query(models.Producto).filter(
        models.Producto.id.in_([i.producto_id for i in datos.items])
    ).all()}

    subtotal = Decimal("0")
    detalles: List[models.DetalleFactura] = []
    for item in datos.items:
        prod = productos_map.get(item.producto_id)
        if prod is None:
            raise ValueError(f"Producto {item.producto_id} no existe")
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
        cliente_id=cliente_id,
        sucursal_id=datos.sucursal_id,
        subtotal=subtotal,
        iva=iva,
        total=total,
        estado="pendiente",
        detalles=detalles,
    )
    db.add(factura)
    db.flush()  # asigna factura.id

    try:
        afectados = reservar_stock(db, factura.id, datos.sucursal_id, datos.items)
    except ValueError:
        db.rollback()
        raise

    db.commit()
    db.refresh(factura)

    for prod_id, suc_id in afectados:
        _publicar_stock(db, prod_id, suc_id)

    return factura


def registrar_pago(db: Session, factura_id: int, metodo: str, estado: str,
                   monto: Decimal, ult4: Optional[str] = None,
                   marca: Optional[str] = None, detalle: Optional[str] = None) -> models.Pago:
    pago = models.Pago(
        factura_id=factura_id,
        metodo=metodo,
        ult4=ult4,
        marca=marca,
        estado=estado,
        monto=monto,
        detalle=detalle,
    )
    db.add(pago)
    if estado == "aprobado":
        db.query(models.Factura).filter(models.Factura.id == factura_id).update(
            {models.Factura.estado: "pagada"}, synchronize_session=False
        )
    db.commit()
    db.refresh(pago)
    return pago


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


# ----------- Admin: inventario -----------

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
    _publicar_stock(db, producto_id, sucursal_id)
    return row


# ----------- Admin: dashboard / metricas -----------

def metricas_dashboard(db: Session) -> dict:
    hoy = date.today()
    ventas_hoy = db.query(
        func.coalesce(func.sum(models.Factura.total), 0)
    ).filter(
        models.Factura.estado == "pagada",
        func.date(models.Factura.fecha) == hoy,
    ).scalar()
    facturas_hoy = db.query(func.count(models.Factura.id)).filter(
        models.Factura.estado == "pagada",
        func.date(models.Factura.fecha) == hoy,
    ).scalar()
    total_facturas = db.query(func.count(models.Factura.id)).filter(
        models.Factura.estado == "pagada"
    ).scalar()
    stock_total = db.query(func.coalesce(func.sum(models.StockSucursal.existencia), 0)).scalar()
    reservado_total = db.query(func.coalesce(func.sum(models.StockSucursal.reservado), 0)).scalar()

    # productos con disponible total bajo el umbral
    sub = (
        db.query(
            models.StockSucursal.producto_id,
            (func.sum(models.StockSucursal.existencia) - func.sum(models.StockSucursal.reservado)).label("disp"),
        )
        .group_by(models.StockSucursal.producto_id)
        .all()
    )
    productos_bajos = sum(1 for _, disp in sub if (disp or 0) < STOCK_BAJO_UMBRAL)

    return {
        "ventas_hoy": float(ventas_hoy or 0),
        "facturas_hoy": int(facturas_hoy or 0),
        "total_facturas": int(total_facturas or 0),
        "stock_total": int(stock_total or 0),
        "reservado_total": int(reservado_total or 0),
        "productos_bajos": productos_bajos,
        "total_productos": db.query(func.count(models.Producto.id)).filter(models.Producto.activo == 1).scalar(),
    }


def stock_por_sucursal_agg(db: Session) -> List[dict]:
    rows = (
        db.query(
            models.Sucursal.nombre,
            func.coalesce(func.sum(models.StockSucursal.existencia), 0),
        )
        .outerjoin(models.StockSucursal, models.StockSucursal.sucursal_id == models.Sucursal.id)
        .group_by(models.Sucursal.id, models.Sucursal.nombre)
        .order_by(models.Sucursal.id)
        .all()
    )
    return [{"sucursal": nombre, "total": int(total or 0)} for nombre, total in rows]


# ----------- Admin: productos (CRUD) -----------

def crear_producto(db: Session, tipo_id: int, nombre: str, descripcion: str,
                   precio: Decimal, imagen_url: Optional[str]) -> models.Producto:
    prod = models.Producto(
        tipo_id=tipo_id,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        imagen_url=imagen_url,
        activo=1,
    )
    db.add(prod)
    db.flush()
    # crea filas de stock en 0 para cada sucursal
    for suc in listar_sucursales(db):
        db.add(models.StockSucursal(producto_id=prod.id, sucursal_id=suc.id, existencia=0, reservado=0))
    db.commit()
    db.refresh(prod)
    return prod


def actualizar_producto(db: Session, producto_id: int, **campos) -> models.Producto | None:
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if prod is None:
        return None
    for k, v in campos.items():
        if v is not None and hasattr(prod, k):
            setattr(prod, k, v)
    db.commit()
    db.refresh(prod)
    return prod


def toggle_producto(db: Session, producto_id: int) -> models.Producto | None:
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if prod is None:
        return None
    prod.activo = 0 if prod.activo else 1
    db.commit()
    db.refresh(prod)
    return prod


def listar_productos_admin(db: Session) -> List[models.Producto]:
    return (
        db.query(models.Producto)
        .options(joinedload(models.Producto.tipo))
        .order_by(models.Producto.id)
        .all()
    )


# ----------- Admin: pedidos -----------

def listar_facturas(db: Session, estado: Optional[str] = None, sucursal_id: Optional[int] = None) -> List[models.Factura]:
    q = db.query(models.Factura).options(
        joinedload(models.Factura.cliente),
        joinedload(models.Factura.sucursal),
    )
    if estado:
        q = q.filter(models.Factura.estado == estado)
    if sucursal_id:
        q = q.filter(models.Factura.sucursal_id == sucursal_id)
    return q.order_by(models.Factura.id.desc()).all()


def facturas_de_cliente(db: Session, cliente_id: int) -> List[models.Factura]:
    return (
        db.query(models.Factura)
        .options(joinedload(models.Factura.sucursal))
        .filter(models.Factura.cliente_id == cliente_id)
        .order_by(models.Factura.id.desc())
        .all()
    )


# ----------- Admin: usuarios -----------

def listar_usuarios(db: Session) -> List[models.Usuario]:
    return (
        db.query(models.Usuario)
        .options(joinedload(models.Usuario.cliente))
        .order_by(models.Usuario.id)
        .all()
    )


def toggle_usuario_activo(db: Session, usuario_id: int) -> models.Usuario | None:
    u = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if u is None:
        return None
    u.activo = 0 if u.activo else 1
    db.commit()
    db.refresh(u)
    return u
