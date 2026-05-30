import asyncio
import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from . import crud, schemas, auth, payments, models
from .db import get_db, engine, Base, SessionLocal
from .pdf import generar_factura_pdf
from .sse import broker

load_dotenv()

BASE_DIR = Path(__file__).parent

app = FastAPI(title="El Membrillo - API")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8080,http://localhost:8081,http://127.0.0.1:8080,http://127.0.0.1:8081",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Imagenes de producto y assets estaticos servidos por la API
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
async def startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[startup] No se pudo asegurar schema: {e}")
    db = SessionLocal()
    try:
        auth.asegurar_admin(db)
    except Exception as e:
        print(f"[startup] No se pudo asegurar admin: {e}")
    finally:
        db.close()
    asyncio.create_task(_limpieza_reservas())


async def _limpieza_reservas() -> None:
    while True:
        await asyncio.sleep(60)
        db = SessionLocal()
        try:
            n = crud.liberar_reservas_vencidas(db)
            if n:
                print(f"[reservas] liberadas {n} reservas vencidas")
        except Exception as e:
            print(f"[reservas] error en limpieza: {e}")
        finally:
            db.close()


# ----------- serializadores -----------

def _producto_detalle(db: Session, prod: models.Producto) -> dict:
    stock = crud.stock_por_sucursal(db, prod.id)
    return {
        "id": prod.id,
        "nombre": prod.nombre,
        "descripcion": prod.descripcion,
        "precio": float(prod.precio),
        "imagen_url": prod.imagen_url,
        "tipo_id": prod.tipo_id,
        "tipo_nombre": prod.tipo.nombre if prod.tipo else None,
        "stock": stock,
        "stock_total": sum(s["existencia"] for s in stock),
        "disponible_total": sum(s["disponible"] for s in stock),
    }


def _factura_json(f: models.Factura, con_items: bool = True) -> dict:
    data = {
        "id": f.id,
        "estado": f.estado,
        "fecha": f.fecha.isoformat() if f.fecha else None,
        "subtotal": float(f.subtotal),
        "iva": float(f.iva),
        "total": float(f.total),
        "cliente": {"nombre": f.cliente.nombre, "nit": f.cliente.nit, "email": f.cliente.email} if f.cliente else None,
        "sucursal": {"id": f.sucursal_id, "nombre": f.sucursal.nombre} if f.sucursal else None,
        "pdf_url": f"/api/facturas/{f.id}/pdf",
    }
    if con_items:
        data["items"] = [{
            "producto_id": d.producto_id,
            "producto": d.producto.nombre if d.producto else None,
            "cantidad": d.cantidad,
            "precio_unit": float(d.precio_unit),
            "subtotal": float(d.subtotal),
        } for d in f.detalles]
    return data


# ----------- Auth -----------

@app.post("/api/auth/registro")
def registro(datos: schemas.RegistroIn, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.email == datos.email).first():
        raise HTTPException(400, "Ya existe una cuenta con ese correo")
    cliente = models.Cliente(nombre=datos.nombre, nit=datos.nit or "CF",
                             email=datos.email, telefono=datos.telefono)
    db.add(cliente)
    db.flush()
    user = models.Usuario(
        nombre=datos.nombre, email=datos.email,
        hashed_password=auth.hash_password(datos.password),
        rol="cliente", cliente_id=cliente.id, activo=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": auth.crear_token(user), "user": auth.serializar_usuario(user)}


@app.post("/api/auth/login")
def login(datos: schemas.LoginIn, db: Session = Depends(get_db)):
    user = auth.autenticar(db, datos.email, datos.password)
    if not user:
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {"token": auth.crear_token(user), "user": auth.serializar_usuario(user)}


@app.get("/api/auth/me")
def me(user: models.Usuario = Depends(auth.bearer_user)):
    return auth.serializar_usuario(user)


# ----------- Catalogo -----------

@app.get("/api/productos")
def api_productos(db: Session = Depends(get_db)):
    return [{**p, "precio": float(p["precio"])} for p in crud.listar_productos(db)]


@app.get("/api/productos/{producto_id}")
def api_producto(producto_id: int, db: Session = Depends(get_db)):
    prod = crud.obtener_producto(db, producto_id)
    if not prod:
        raise HTTPException(404, "Producto no encontrado")
    return _producto_detalle(db, prod)


@app.get("/api/sucursales")
def api_sucursales(db: Session = Depends(get_db)):
    return [{"id": s.id, "nombre": s.nombre, "direccion": s.direccion, "telefono": s.telefono}
            for s in crud.listar_sucursales(db)]


@app.get("/api/tipos")
def api_tipos(db: Session = Depends(get_db)):
    return [{"id": t.id, "nombre": t.nombre} for t in crud.listar_tipos(db)]


@app.get("/api/stock/{producto_id}")
def api_stock(producto_id: int, db: Session = Depends(get_db)):
    return {
        "producto_id": producto_id,
        "stock_total": crud.stock_total_producto(db, producto_id),
        "por_sucursal": crud.stock_por_sucursal(db, producto_id),
    }


# ----------- Compra: checkout + pago -----------

@app.post("/api/checkout")
def checkout(datos: schemas.CheckoutIn, db: Session = Depends(get_db),
             user: Optional[models.Usuario] = Depends(auth.usuario_opcional)):
    if not datos.items:
        raise HTTPException(400, "Carrito vacío")
    cliente_id = user.cliente_id if (user and user.cliente_id) else None
    if user and not datos.email:
        datos.email = user.email
    try:
        factura = crud.crear_factura(db, datos, cliente_id=cliente_id)
    except ValueError as e:
        raise HTTPException(409, str(e))
    if user and not user.cliente_id:
        user.cliente_id = factura.cliente_id
        db.commit()
    return {"factura_id": factura.id, "total": float(factura.total)}


@app.get("/api/facturas/{factura_id}")
def api_factura(factura_id: int, db: Session = Depends(get_db)):
    f = crud.obtener_factura(db, factura_id)
    if not f:
        raise HTTPException(404)
    return _factura_json(f)


@app.post("/api/pago/{factura_id}")
def pago(factura_id: int, datos: schemas.PagoIn, db: Session = Depends(get_db)):
    crud.liberar_reservas_vencidas(db)
    factura = crud.obtener_factura(db, factura_id)
    if not factura:
        raise HTTPException(404)
    if factura.estado != "pendiente":
        return {"estado": "expirada", "factura": _factura_json(factura),
                "error": "La reserva expiró o la factura ya no está pendiente."}

    monto = Decimal(str(factura.total))

    if datos.metodo == "contra_entrega":
        crud.confirmar_reservas(db, factura_id)
        crud.registrar_pago(db, factura_id, "contra_entrega", "aprobado", monto,
                            detalle="Pago contra entrega en sucursal")
        factura = crud.obtener_factura(db, factura_id)
        generar_factura_pdf(factura)
        return {"estado": "aprobado", "factura": _factura_json(factura)}

    validacion = payments.validar_tarjeta(datos.numero or "", datos.expiracion or "", datos.cvv or "")
    if not validacion.ok:
        return JSONResponse({"estado": "invalido", "error": validacion.error}, status_code=400)

    numero_limpio = "".join(ch for ch in (datos.numero or "") if ch.isdigit())
    aprobado = numero_limpio == "4111111111111111" or payments.procesar_pago(validacion)

    if aprobado:
        crud.confirmar_reservas(db, factura_id)
        crud.registrar_pago(db, factura_id, "tarjeta", "aprobado", monto,
                            ult4=validacion.ult4, marca=validacion.marca, detalle="Pago aprobado")
        factura = crud.obtener_factura(db, factura_id)
        generar_factura_pdf(factura)
        return {"estado": "aprobado", "factura": _factura_json(factura)}

    crud.liberar_reservas(db, factura_id)
    crud.registrar_pago(db, factura_id, "tarjeta", "rechazado", monto,
                        ult4=validacion.ult4, marca=validacion.marca, detalle="Pago rechazado")
    factura = crud.obtener_factura(db, factura_id)
    return JSONResponse(
        {"estado": "rechazado", "factura": _factura_json(factura),
         "error": "El pago fue rechazado por el banco emisor. Tu reserva se liberó."},
        status_code=402,
    )


@app.get("/api/facturas/{factura_id}/pdf")
def factura_pdf(factura_id: int):
    path = BASE_DIR / "static" / "facturas" / f"factura_{factura_id:06d}.pdf"
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(str(path), media_type="application/pdf", filename=path.name)


@app.get("/api/mis-facturas")
def mis_facturas(db: Session = Depends(get_db), user: models.Usuario = Depends(auth.bearer_user)):
    if not user.cliente_id:
        return []
    return [_factura_json(f, con_items=False) for f in crud.facturas_de_cliente(db, user.cliente_id)]


# ----------- Admin -----------

@app.get("/api/admin/metricas")
def admin_metricas(db: Session = Depends(get_db), _: models.Usuario = Depends(auth.bearer_admin)):
    return crud.metricas_dashboard(db)


@app.get("/api/admin/grafica")
def admin_grafica(db: Session = Depends(get_db), _: models.Usuario = Depends(auth.bearer_admin)):
    return crud.stock_por_sucursal_agg(db)


@app.get("/api/admin/inventario")
def admin_inventario(db: Session = Depends(get_db), _: models.Usuario = Depends(auth.bearer_admin)):
    productos = crud.listar_productos(db)
    sucursales = crud.listar_sucursales(db)
    celdas = {p["id"]: {s.id: {"existencia": 0, "reservado": 0} for s in sucursales} for p in productos}
    for r in db.query(models.StockSucursal).all():
        if r.producto_id in celdas and r.sucursal_id in celdas[r.producto_id]:
            celdas[r.producto_id][r.sucursal_id] = {"existencia": r.existencia, "reservado": r.reservado}
    return {
        "sucursales": [{"id": s.id, "nombre": s.nombre} for s in sucursales],
        "productos": [{"id": p["id"], "nombre": p["nombre"], "imagen_url": p["imagen_url"],
                       "tipo_nombre": p["tipo_nombre"],
                       "celdas": [{"sucursal_id": s.id, **celdas[p["id"]][s.id]} for s in sucursales]}
                      for p in productos],
    }


@app.post("/api/admin/stock")
def admin_stock(datos: schemas.StockAdminIn, db: Session = Depends(get_db),
                _: models.Usuario = Depends(auth.bearer_admin)):
    try:
        row = crud.ajustar_stock(db, datos.producto_id, datos.sucursal_id, datos.existencia)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"producto_id": datos.producto_id, "sucursal_id": datos.sucursal_id,
            "existencia": row.existencia, "reservado": row.reservado, "disponible": row.disponible}


@app.get("/api/admin/productos")
def admin_productos(db: Session = Depends(get_db), _: models.Usuario = Depends(auth.bearer_admin)):
    return [{"id": p.id, "nombre": p.nombre, "descripcion": p.descripcion,
             "precio": float(p.precio), "imagen_url": p.imagen_url,
             "tipo_id": p.tipo_id, "tipo_nombre": p.tipo.nombre if p.tipo else None,
             "activo": bool(p.activo)} for p in crud.listar_productos_admin(db)]


@app.post("/api/admin/productos")
def admin_producto_crear(datos: schemas.ProductoIn, db: Session = Depends(get_db),
                         _: models.Usuario = Depends(auth.bearer_admin)):
    p = crud.crear_producto(db, datos.tipo_id, datos.nombre, datos.descripcion or "",
                            Decimal(str(datos.precio)), datos.imagen_url)
    return {"id": p.id}


@app.put("/api/admin/productos/{producto_id}")
def admin_producto_editar(producto_id: int, datos: schemas.ProductoIn, db: Session = Depends(get_db),
                          _: models.Usuario = Depends(auth.bearer_admin)):
    p = crud.actualizar_producto(db, producto_id, tipo_id=datos.tipo_id, nombre=datos.nombre,
                                 descripcion=datos.descripcion, precio=Decimal(str(datos.precio)),
                                 imagen_url=datos.imagen_url)
    if not p:
        raise HTTPException(404)
    return {"id": p.id}


@app.post("/api/admin/productos/{producto_id}/toggle")
def admin_producto_toggle(producto_id: int, db: Session = Depends(get_db),
                          _: models.Usuario = Depends(auth.bearer_admin)):
    p = crud.toggle_producto(db, producto_id)
    if not p:
        raise HTTPException(404)
    return {"id": p.id, "activo": bool(p.activo)}


@app.get("/api/admin/pedidos")
def admin_pedidos(estado: Optional[str] = None, sucursal_id: Optional[int] = None,
                  db: Session = Depends(get_db), _: models.Usuario = Depends(auth.bearer_admin)):
    facturas = crud.listar_facturas(db, estado=estado, sucursal_id=sucursal_id)
    return [{
        "id": f.id, "estado": f.estado, "total": float(f.total),
        "fecha": f.fecha.isoformat() if f.fecha else None,
        "cliente": f.cliente.nombre if f.cliente else None,
        "sucursal": f.sucursal.nombre if f.sucursal else None,
    } for f in facturas]


@app.get("/api/admin/pedidos/{factura_id}")
def admin_pedido(factura_id: int, db: Session = Depends(get_db),
                 _: models.Usuario = Depends(auth.bearer_admin)):
    f = crud.obtener_factura(db, factura_id)
    if not f:
        raise HTTPException(404)
    return _factura_json(f)


@app.get("/api/admin/usuarios")
def admin_usuarios(db: Session = Depends(get_db), _: models.Usuario = Depends(auth.bearer_admin)):
    return [{"id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol,
             "cliente": u.cliente.nombre if u.cliente else None, "activo": bool(u.activo)}
            for u in crud.listar_usuarios(db)]


@app.post("/api/admin/usuarios/{usuario_id}/toggle")
def admin_usuario_toggle(usuario_id: int, db: Session = Depends(get_db),
                         _: models.Usuario = Depends(auth.bearer_admin)):
    u = crud.toggle_usuario_activo(db, usuario_id)
    if not u:
        raise HTTPException(404)
    return {"id": u.id, "activo": bool(u.activo)}


# ----------- SSE (publico) -----------

@app.get("/api/stream/stock")
async def stream_stock(request: Request):
    queue = await broker.subscribe()

    async def event_generator():
        try:
            yield {"event": "ready", "data": json.dumps({"ok": True})}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    # ping cada 10s para mantener viva la conexion (proxies/navegador)
                    payload = await asyncio.wait_for(queue.get(), timeout=10)
                    yield {"event": "stock_update", "data": payload}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            await broker.unsubscribe(queue)

    return EventSourceResponse(
        event_generator(),
        ping=15,
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/health")
def health():
    return {"ok": True}


# Identidad del pod/instancia que atiende la peticion (para demo Blue-Green en K8s)
POD_NAME = os.getenv("POD_NAME") or os.getenv("HOSTNAME") or "local"
APP_COLOR = os.getenv("APP_COLOR", "")
APP_VERSION = os.getenv("APP_VERSION", "dev")


@app.get("/api/info")
def info():
    return {"pod": POD_NAME, "color": APP_COLOR, "version": APP_VERSION}
