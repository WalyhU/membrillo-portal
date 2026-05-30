# INSTRUCCIONES — Portal "El Membrillo" (Jaleas Artesanales S.A.)

> Caso ATI — Semestre 9. Documento personal, paso a paso, escrito para ti.
> Todo el código ya está generado dentro de `membrillo_portal/`. Tú solo ejecutas.

---

## 0. Lo que vas a entregar

1. **Sitio web funcional** con catálogo, carrito, checkout, **pago con tarjeta simulado** y factura PDF.
2. **Stock en tiempo real** (SSE) que se actualiza solo cuando cambian existencias o reservas.
3. **Reserva de stock**: al iniciar el pago el stock se reserva 15 min (libera solo si no pagas). El catálogo muestra **disponible = existencia − reservado**.
4. **Login y roles**: clientes se registran y ven su historial; el **panel admin** está protegido por rol.
5. **Panel admin completo** (páginas separadas): dashboard con métricas + gráfica, inventario, CRUD de productos, pedidos y usuarios.
6. **Modelo de datos propio** en MySQL (Docker), 10 tablas: las 7 originales (`tipo_producto`, `producto`, `sucursal`, `stock_sucursal`, `cliente`, `factura`, `detalle_factura`) + `usuario`, `pago`, `reserva`.
7. **Demo en vivo** durante la presentación (simulador de ventas que baja stock en pantalla).
8. **Presentación** con la propuesta de la solución (outline en `membrillo_portal/presentacion.md`).

> **Credenciales admin por defecto** (se crean solas al iniciar la app): `admin@membrillo.gt` / `membrillo123` (configurables en `.env`).
> **Tarjeta de prueba** que siempre aprueba el pago: `4111 1111 1111 1111`, cualquier fecha futura, CVV `123`.

Cumple las 5 restricciones del PDF:
- No se programó "desde cero" — se hizo con vibecoding asistido.
- Modelo de ventas con las 4 tablas pedidas (y se extendió con sucursales y stock).
- Sitio interactúa con el modelo y refleja stock en tiempo real (SSE).
- Listo antes del 11 de abril 2026 (verificar con catedrático la fecha real).
- Hay slides + solución propuesta.

---

## 1. Requisitos previos (instala una sola vez)

### 1.1 Docker Desktop
1. Descarga: https://www.docker.com/products/docker-desktop/
2. Instala. Reinicia si lo pide.
3. Abre Docker Desktop y déjalo corriendo (icono de ballena en la bandeja del sistema).
4. Verifica en PowerShell:
   ```powershell
   docker --version
   docker compose version
   ```

### 1.2 Python 3.11 o superior
1. Descarga: https://www.python.org/downloads/ (marca "Add to PATH" en el instalador).
2. Verifica:
   ```powershell
   python --version
   ```

### 1.3 ngrok (solo para demo pública desde fuera de tu red)
1. Crea cuenta gratis en https://ngrok.com/
2. Descarga el `.exe`, agrégalo al PATH o déjalo en la carpeta del proyecto.
3. Pega tu authtoken: `ngrok config add-authtoken <TU_TOKEN>`

---

## 2. Levantar la base de datos (Docker)

Abre PowerShell **en la carpeta del proyecto**:

```powershell
cd "E:\UMG\SEMESTRE 9\ATI\membrillo_portal"
docker compose up -d
```

Esto levanta:
- `membrillo_mysql` — MySQL 8 en `localhost:3306` (root / membrillo).
- `membrillo_pma` — phpMyAdmin en http://localhost:8082.

El **schema** y el **seed** se cargan automáticamente la primera vez (Docker corre los archivos de `sql/` al inicializar el volumen).

### Verificar que cargó bien
1. Abre http://localhost:8082
2. Servidor: `mysql`, usuario: `root`, contraseña: `membrillo`.
3. Selecciona `membrillo_db`. Deberías ver las 10 tablas:
   - `tipo_producto` → 4 filas
   - `producto` → 7 filas
   - `sucursal` → 6 filas
   - `stock_sucursal` → 42 filas (7×6), ahora con columna `reservado`
   - `cliente` → 1 fila (Consumidor Final)
   - `usuario` → 1 fila (admin, se crea al iniciar la app)
   - `factura`, `detalle_factura`, `pago`, `reserva` → vacías

> **Si el schema no cargó** (puerto 3306 ya estaba en uso por otro MySQL local), corre el fallback:
> ```powershell
> python -m venv .venv
> .venv\Scripts\activate
> pip install -r requirements.txt
> python scripts\init_db.py
> ```

---

## 3. Arquitectura: 3 servicios sobre una sola API

El portal ahora está **separado en servicios distintos**, cada uno en su propia página (origen), todos contra la **misma API**:

```
[web :8080  e-commerce]  ─┐
                          ├── fetch ──> [api :8000  FastAPI JSON] ──> [mysql :3306]
[admin :8081  panel]     ─┘                  SSE /api/stream/stock (público)
```

| Servicio | URL | Qué es |
|---|---|---|
| **E-commerce** | http://localhost:8080 | Tienda para clientes (catálogo, carrito, pago) |
| **Admin** | http://localhost:8081 | Panel de administración (login propio) |
| **API** | http://localhost:8000/api | Backend JSON (FastAPI). Docs: http://localhost:8000/docs |
| **phpMyAdmin** | http://localhost:8082 | Ver la base de datos |

### Opción A — Todo en Docker (recomendado, un solo comando)

```powershell
cd "E:\UMG\SEMESTRE 9\ATI\membrillo_portal"
docker compose up -d --build
```

Levanta mysql, api, web, admin y phpMyAdmin. Abre **http://localhost:8080** (tienda) y **http://localhost:8081** (admin).

### Opción B — API local + fronts estáticos (desarrollo)

```powershell
cd "E:\UMG\SEMESTRE 9\ATI\membrillo_portal"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# 1) API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 2) en otras terminales, servir los fronts estáticos:
python -m http.server 8080 --directory web
python -m http.server 8081 --directory admin
```

> Los fronts usan `assets/config.js` (`window.API_BASE`) para ubicar la API. Por defecto apunta a `http://localhost:8000/api`. Si cambias el host/puerto de la API, edita ese archivo en `web/assets/` y `admin/assets/`.

---

## 4. Probar el flujo completo

**Tienda — http://localhost:8080**
1. **Catálogo** — 7 productos con su **disponible**. Filtra por tipo con los chips.
2. **Registro** clic en "Ingresar" → "Regístrate" → crea una cuenta (queda la sesión guardada en el navegador).
3. **Detalle** clic en un producto → disponibilidad por las 6 sucursales.
4. **Carrito** agrega productos (el carrito vive en el navegador) → "Carrito" → confirma datos y sucursal → "Continuar al pago".
5. **Reserva**: al entrar al pago, el stock se reservó. Abre el catálogo en otra pestaña: el **disponible bajó** aunque aún no pagas.
6. **Pago** tarjeta de prueba `4111 1111 1111 1111`, exp `12/29`, CVV `123` → "Pagar". La tarjeta animada refleja tus datos.
7. **Éxito** página con confeti → "Descargar PDF". La existencia bajó de verdad.
8. **Mi cuenta** → tu pedido aparece con estado "pagada".

**Admin — http://localhost:8081** (servicio aparte, login propio)
9. Entra con `admin@membrillo.gt` / `membrillo123`:
   - **Dashboard**: métricas + gráfica de stock por sucursal + feed de ventas en vivo (SSE).
   - **Inventario**: matriz editable (cambia un valor → se guarda solo).
   - **Productos**: crea/edita/activa-desactiva (modal).
   - **Pedidos**: revisa la factura recién creada y su detalle.
   - **Usuarios**: aparece el cliente que registraste.
10. **SSE en vivo**: abre la tienda (:8080) y el inventario admin (:8081) en dos pestañas. Una venta baja el **disponible** en la tienda y destella la celda del admin — **sin recargar**.

---

## 5. Demo SSE para la presentación

Mientras estás presentando el catálogo en pantalla, en otra terminal:

```powershell
.venv\Scripts\activate
pip install requests   # solo la primera vez
python scripts\simulate_sales.py --n 30 --delay 2
```

El script pega directo a la **API** (`/api/checkout` → `/api/pago`) con la tarjeta de prueba. Con la tienda (:8080) o el inventario admin (:8081) abiertos, verás los badges de stock bajando en vivo, con destello. **Esto es el factor wow**.

---

## 6. Demo pública con ngrok (opcional)

Si la demo se hace desde otra computadora o desde el celular del catedrático:

```powershell
ngrok http 8000
```

Copia la URL `https://xxxx.ngrok-free.app` y compártela. Funciona desde cualquier red.

> El URL cambia cada vez que reinicias ngrok en plan gratuito. Genéralo justo antes de presentar.

---

## 7. Reset / limpieza

- **Reiniciar BD desde cero** (borra todos los datos):
  ```powershell
  docker compose down -v
  docker compose up -d
  ```
- **Detener todo**: `docker compose down`
- **Detener app**: Ctrl+C en la terminal de uvicorn.

---

## 8. Estructura de lo entregado

```
membrillo_portal/
  app/                API JSON (FastAPI) — :8000
    main.py           endpoints /api/* (auth, catálogo, checkout, pago, admin, SSE)
    models.py         ORM 10 tablas
    crud.py           lógica: reservas, facturación, métricas, CRUD
    auth.py           bcrypt + tokens (Bearer) + dependencias de rol
    payments.py       validación Luhn + pasarela simulada
    sse.py / pdf.py   broker SSE / factura PDF
  web/                E-commerce estático (nginx) — :8080
    index/producto/carrito/pago/compra-exitosa/login/registro/mi-cuenta.html
    assets/           config.js + api.js + design system compartido
  admin/              Panel admin estático (nginx) — :8081
    index(dashboard)/inventario/productos/pedidos/pedido-detalle/usuarios/login.html
    assets/           config.js + admin-api.js + admin-shell.js + design system
  sql/                schema + seed (auto-load por Docker)
  scripts/            init_db.py (fallback) + simulate_sales.py (usa la API)
  docker-compose.yml  mysql + api + web + admin + phpMyAdmin
  Dockerfile          Imagen de la API
  requirements.txt
  .env.example        DATABASE_URL, SECRET_KEY, ALLOWED_ORIGINS, ADMIN_EMAIL/PASSWORD
  DESIGN_BRIEF_v2.md  brief para rediseño (Claude Design)
  presentacion.md     Outline de slides
  README.md           Doc técnica
```

---

## 9. Para la presentación (8 puntos de zona)

Lee `membrillo_portal/presentacion.md` — trae el outline de slides ya armado:
1. Problema (cierre pandémico, -85% ventas).
2. Por qué un portal es la solución.
3. Restricciones (no programar desde cero → vibecoding).
4. Stack y arquitectura (FastAPI + MySQL en Docker + SSE).
5. Modelo de datos (7 tablas, diagrama).
6. Demo en vivo (pasos 4 y 5 de este archivo).
7. Despliegue (Docker → cualquier hosting con un comando).
8. Tiempo y costo (días, no 6 meses; 0 USD para el demo).

**Ensaya 2 veces antes**. Cronometra: 8–10 min máx. Pide a un compañero que abra `simulate_sales.py` en otra máquina mientras tú presentas el catálogo.

---

## 10. Checklist final pre-presentación

- [ ] Docker Desktop corriendo
- [ ] `docker compose up -d` levantado y phpMyAdmin abre
- [ ] `uvicorn` corriendo, http://localhost:8000 abre
- [ ] Registraste un cliente y entró su sesión
- [ ] Compraste con la tarjeta de prueba, vi la reserva bajar el disponible, pago aprobado, factura PDF descargó
- [ ] Login admin funciona y el panel (`/admin`) muestra dashboard, inventario, productos, pedidos, usuarios
- [ ] SSE funciona (probaste con dos pestañas)
- [ ] `simulate_sales.py` ejecuta sin errores
- [ ] ngrok generado y URL copiada
- [ ] Slides repasados (`presentacion.md`)
- [ ] Laptop cargada, cargador a la mano
- [ ] Plan B: video grabado de la demo por si falla la red

---

## 11. Si algo falla

| Problema | Solución |
|---|---|
| Puerto 3306 en uso | Detén MySQL local: `Stop-Service MySQL80` (o como se llame) |
| Puerto 8000 en uso | Cambia `--port 8001` en uvicorn |
| `docker: command not found` | Docker Desktop no está corriendo o no está en PATH |
| `pip` falla | Activa venv: `.venv\Scripts\activate` |
| Tablas vacías | `docker compose down -v` y `up -d` otra vez |
| SSE no actualiza | Revisa la consola del navegador (F12) — debe decir "Stock en vivo conectado" |
| ngrok caduca | Regenera: `ngrok http 8000` |

---

**Fecha de presentación según el PDF:** 11 de abril 2026 (ya pasó). **Confirma con el catedrático la fecha real antes de presentar.**
