# El Membrillo — Portal de Ventas

Solución al caso ATI "Jaleas Artesanales S.A.": portal web con catálogo, módulo de ventas y stock en tiempo real.

## Stack

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2 + Pydantic
- **Base de datos**: MySQL 8 (Docker)
- **Frontend**: Jinja2 + Bootstrap 5 + EventSource (SSE)
- **PDF**: reportlab
- **Real-time**: Server-Sent Events (sse-starlette)

## Arquitectura

```
[Cliente Web] --HTTP--> [FastAPI :8000] --SQLAlchemy--> [Docker MySQL :3306]
       ^                       |                          (volumen persistente)
       |--SSE /stream/stock----|
```

## Modelo de datos

Cumple la restricción 2 del PDF (tablas mínimas) y la extiende con sucursales:

- `tipo_producto` (4 filas seed)
- `producto` (7 filas)
- `sucursal` (6 filas — las del PDF)
- `stock_sucursal` (relación M:M con existencia, único `producto+sucursal`)
- `cliente`
- `factura` + `detalle_factura`

Ver `sql/01_schema.sql`.

## Endpoints clave

| Ruta | Método | Descripción |
|---|---|---|
| `/` | GET | Catálogo |
| `/producto/{id}` | GET | Detalle + stock por sucursal |
| `/carrito` | GET/POST | Carrito en sesión cookie |
| `/checkout` | POST | Crea factura + descuenta stock + emite SSE |
| `/factura/{id}/ok` | GET | Página éxito |
| `/factura/{id}/pdf` | GET | Descarga PDF |
| `/admin` | GET/POST | Matriz stock editable |
| `/api/productos` | GET | JSON catálogo |
| `/api/stock/{id}` | GET | JSON stock |
| `/stream/stock` | GET | **SSE** stock en vivo |

## Cómo correr

Ver `../INSTRUCCIONES.md` (paso a paso para el usuario final).

Resumen rápido:

```bash
docker compose up -d
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Abrir http://localhost:8000

## Demo SSE

```bash
python scripts/simulate_sales.py --n 30 --delay 2
```

## Restricciones del PDF — cómo se cumplen

| # | Restricción | Cumplimiento |
|---|---|---|
| 1 | No programar desde cero | Vibecoding (código asistido por AI) sobre frameworks consolidados (FastAPI, SQLAlchemy, Bootstrap) |
| 2 | Tablas mín. (tipo_producto, producto, cliente, factura) | ✓ Las 4 + sucursales + stock_sucursal + detalle_factura |
| 3 | Portal interactúa con BD y refleja stock tiempo real | ✓ FastAPI + ORM + SSE empuja cambios al navegador |
| 4 | Fecha 11-abr-2026 | Listo antes |
| 5 | Presentación + solución | `presentacion.md` |
