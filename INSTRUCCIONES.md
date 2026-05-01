# INSTRUCCIONES — Portal "El Membrillo" (Jaleas Artesanales S.A.)

> Caso ATI — Semestre 9. Documento personal, paso a paso, escrito para ti.
> Todo el código ya está generado dentro de `membrillo_portal/`. Tú solo ejecutas.

---

## 0. Lo que vas a entregar

1. **Sitio web funcional** con catálogo, carrito, checkout y factura PDF.
2. **Stock en tiempo real** (SSE) que se actualiza solo cuando cambian existencias.
3. **Modelo de datos propio** en MySQL (Docker) con 7 tablas: `tipo_producto`, `producto`, `sucursal`, `stock_sucursal`, `cliente`, `factura`, `detalle_factura`.
4. **Demo en vivo** durante la presentación (con simulador de ventas que baja stock en pantalla).
5. **Presentación** con la propuesta de la solución (outline incluido en `membrillo_portal/presentacion.md`).

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
- `membrillo_pma` — phpMyAdmin en http://localhost:8080.

El **schema** y el **seed** se cargan automáticamente la primera vez (Docker corre los archivos de `sql/` al inicializar el volumen).

### Verificar que cargó bien
1. Abre http://localhost:8080
2. Servidor: `mysql`, usuario: `root`, contraseña: `membrillo`.
3. Selecciona `membrillo_db`. Deberías ver las 7 tablas con datos:
   - `tipo_producto` → 4 filas
   - `producto` → 7 filas
   - `sucursal` → 6 filas
   - `stock_sucursal` → 42 filas (7×6)
   - `cliente` → 1 fila (Consumidor Final)
   - `factura`, `detalle_factura` → vacías

> **Si el schema no cargó** (puerto 3306 ya estaba en uso por otro MySQL local), corre el fallback:
> ```powershell
> python -m venv .venv
> .venv\Scripts\activate
> pip install -r requirements.txt
> python scripts\init_db.py
> ```

---

## 3. Levantar la aplicación FastAPI

### Opción A — Local (recomendado para desarrollo y demo)

```powershell
cd "E:\UMG\SEMESTRE 9\ATI\membrillo_portal"

# crear entorno virtual una sola vez
python -m venv .venv
.venv\Scripts\activate

# instalar dependencias una sola vez
pip install -r requirements.txt

# copiar config
copy .env.example .env

# correr el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abre http://localhost:8000

### Opción B — Todo en Docker (un solo comando)

```powershell
docker compose --profile full up --build
```

Esto agrega el servicio `app` al stack. Más limpio pero recompila cada cambio.

---

## 4. Probar el flujo completo

1. **Catálogo** http://localhost:8000 — debes ver 7 productos con stock.
2. **Detalle** clic en cualquiera → ves stock por las 6 sucursales.
3. **Carrito** agrega 2 productos → ve a `/carrito` → llena nombre y elige sucursal → "Confirmar y generar factura".
4. **Factura** sale página de éxito → "Descargar PDF" → revisa el PDF.
5. **Stock bajó**: vuelve al catálogo y al detalle del producto que compraste — el número debe ser menor.
6. **Admin** http://localhost:8000/admin — matriz editable. Cambia un valor y guarda.
7. **SSE en vivo**: abre dos pestañas (catálogo y admin). Cambia stock en admin → la pestaña del catálogo se actualiza sola **sin recargar**, con un destello amarillo.

---

## 5. Demo SSE para la presentación

Mientras estás presentando el catálogo en pantalla, en otra terminal:

```powershell
.venv\Scripts\activate
pip install requests   # solo la primera vez
python scripts\simulate_sales.py --n 30 --delay 2
```

El script genera 30 ventas con clientes aleatorios. Verás en pantalla los badges de stock bajando en vivo, con destello. **Esto es el factor wow**.

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
  app/                FastAPI (rutas, ORM, CRUD, SSE, PDF, templates)
  sql/                schema + seed (auto-load por Docker)
  scripts/            init_db.py (fallback) + simulate_sales.py (demo)
  docker-compose.yml  MySQL + phpMyAdmin (+ app opcional)
  Dockerfile          Imagen FastAPI
  requirements.txt
  .env.example
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
- [ ] Compraste un producto de prueba, factura PDF descargó
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
