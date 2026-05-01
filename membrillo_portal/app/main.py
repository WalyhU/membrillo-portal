import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from . import crud, schemas
from .db import get_db, engine, Base
from .pdf import generar_factura_pdf
from .sse import broker

load_dotenv()

BASE_DIR = Path(__file__).parent

app = FastAPI(title="El Membrillo - Portal de Ventas")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-secret-membrillo"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
async def startup() -> None:
    # Crea tablas si no existen (defensa, lo normal es que docker init scripts las creen)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[startup] No se pudo asegurar schema: {e}")


def _carrito(request: Request) -> list[dict]:
    return request.session.setdefault("carrito", [])


def _guardar_carrito(request: Request, carrito: list[dict]) -> None:
    request.session["carrito"] = carrito


# ----------- Vistas -----------

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    productos = crud.listar_productos(db)
    tipos = crud.listar_tipos(db)
    return templates.TemplateResponse("catalogo.html", {
        "request": request,
        "productos": productos,
        "tipos": tipos,
        "carrito_count": sum(i["cantidad"] for i in _carrito(request)),
    })


@app.get("/producto/{producto_id}", response_class=HTMLResponse)
def detalle(producto_id: int, request: Request, db: Session = Depends(get_db)):
    producto = crud.obtener_producto(db, producto_id)
    if not producto:
        raise HTTPException(404, "Producto no encontrado")
    stock = crud.stock_por_sucursal(db, producto_id)
    total = crud.stock_total_producto(db, producto_id)
    return templates.TemplateResponse("producto.html", {
        "request": request,
        "producto": producto,
        "stock": stock,
        "stock_total": total,
        "carrito_count": sum(i["cantidad"] for i in _carrito(request)),
    })


@app.post("/carrito/agregar")
def agregar_carrito(request: Request, producto_id: int = Form(...), cantidad: int = Form(1)):
    if cantidad < 1:
        raise HTTPException(400, "Cantidad invalida")
    carrito = _carrito(request)
    for item in carrito:
        if item["producto_id"] == producto_id:
            item["cantidad"] += cantidad
            break
    else:
        carrito.append({"producto_id": producto_id, "cantidad": cantidad})
    _guardar_carrito(request, carrito)
    return RedirectResponse("/carrito", status_code=303)


@app.post("/carrito/quitar")
def quitar_carrito(request: Request, producto_id: int = Form(...)):
    carrito = [i for i in _carrito(request) if i["producto_id"] != producto_id]
    _guardar_carrito(request, carrito)
    return RedirectResponse("/carrito", status_code=303)


@app.get("/carrito", response_class=HTMLResponse)
def ver_carrito(request: Request, db: Session = Depends(get_db)):
    carrito = _carrito(request)
    items = []
    total = 0
    for it in carrito:
        prod = crud.obtener_producto(db, it["producto_id"])
        if not prod:
            continue
        sub = float(prod.precio) * it["cantidad"]
        total += sub
        items.append({
            "producto": prod,
            "cantidad": it["cantidad"],
            "subtotal": sub,
        })
    sucursales = crud.listar_sucursales(db)
    return templates.TemplateResponse("carrito.html", {
        "request": request,
        "items": items,
        "total": total,
        "sucursales": sucursales,
        "carrito_count": sum(i["cantidad"] for i in carrito),
    })


@app.post("/checkout")
def checkout(
    request: Request,
    nombre: str = Form(...),
    nit: str = Form("CF"),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    direccion: Optional[str] = Form(None),
    sucursal_id: int = Form(...),
    db: Session = Depends(get_db),
):
    carrito = _carrito(request)
    if not carrito:
        return RedirectResponse("/", status_code=303)

    datos = schemas.CheckoutIn(
        nombre=nombre,
        nit=nit or "CF",
        email=email or None,
        telefono=telefono or None,
        direccion=direccion or None,
        sucursal_id=sucursal_id,
        items=[schemas.ItemCarrito(**i) for i in carrito],
    )
    try:
        factura = crud.crear_factura(db, datos)
    except ValueError as e:
        return templates.TemplateResponse("carrito.html", {
            "request": request,
            "items": [],
            "total": 0,
            "sucursales": crud.listar_sucursales(db),
            "carrito_count": 0,
            "error": str(e),
        }, status_code=400)

    pdf_path = generar_factura_pdf(factura)
    request.session["carrito"] = []
    return RedirectResponse(f"/factura/{factura.id}/ok", status_code=303)


@app.get("/factura/{factura_id}/ok", response_class=HTMLResponse)
def factura_ok(factura_id: int, request: Request, db: Session = Depends(get_db)):
    factura = crud.obtener_factura(db, factura_id)
    if not factura:
        raise HTTPException(404)
    return templates.TemplateResponse("factura_ok.html", {
        "request": request,
        "factura": factura,
        "pdf_url": f"/factura/{factura_id}/pdf",
        "carrito_count": 0,
    })


@app.get("/factura/{factura_id}/pdf")
def factura_pdf(factura_id: int):
    path = Path(__file__).parent / "static" / "facturas" / f"factura_{factura_id:06d}.pdf"
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(str(path), media_type="application/pdf", filename=path.name)


# ----------- Admin -----------

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, db: Session = Depends(get_db)):
    productos = crud.listar_productos(db)
    sucursales = crud.listar_sucursales(db)
    matriz = {}
    for p in productos:
        matriz[p["id"]] = {s.id: 0 for s in sucursales}
    from .models import StockSucursal
    rows = db.query(StockSucursal).all()
    for r in rows:
        if r.producto_id in matriz:
            matriz[r.producto_id][r.sucursal_id] = r.existencia
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "productos": productos,
        "sucursales": sucursales,
        "matriz": matriz,
        "carrito_count": sum(i["cantidad"] for i in _carrito(request)),
    })


@app.post("/admin/stock")
def admin_stock(producto_id: int = Form(...), sucursal_id: int = Form(...), existencia: int = Form(...), db: Session = Depends(get_db)):
    crud.ajustar_stock(db, producto_id, sucursal_id, existencia)
    return RedirectResponse("/admin", status_code=303)


# ----------- API JSON -----------

@app.get("/api/productos")
def api_productos(db: Session = Depends(get_db)):
    return JSONResponse([
        {**p, "precio": float(p["precio"])} for p in crud.listar_productos(db)
    ])


@app.get("/api/stock/{producto_id}")
def api_stock(producto_id: int, db: Session = Depends(get_db)):
    return {
        "producto_id": producto_id,
        "stock_total": crud.stock_total_producto(db, producto_id),
        "por_sucursal": crud.stock_por_sucursal(db, producto_id),
    }


# ----------- SSE -----------

@app.get("/stream/stock")
async def stream_stock(request: Request):
    queue = await broker.subscribe()

    async def event_generator():
        try:
            yield {"event": "ready", "data": json.dumps({"ok": True})}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15)
                    yield {"event": "stock_update", "data": payload}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            await broker.unsubscribe(queue)

    return EventSourceResponse(event_generator())
