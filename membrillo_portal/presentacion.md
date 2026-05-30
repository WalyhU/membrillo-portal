# Presentación — Portal "El Membrillo"

> Outline de slides para la exposición. ~8–10 minutos. 8 puntos de zona.

---

## Slide 1 — Portada
- **Título**: "El Membrillo" — Portal de Ventas en línea
- Jaleas Artesanales S.A.
- Tu nombre / grupo / fecha

## Slide 2 — El Problema
- Pandemia marzo 2020 → cierre total
- Ventas cayeron **85%** en 3 meses
- Sin presencia digital, los clientes no podían comprar
- Las 6 sucursales aisladas, sin movilización departamental

## Slide 3 — La conversación con la Lic. Guzmán
- Propuesta inicial: "necesito 6 meses para un portal"
- Respuesta: "totalmente fuera de la realidad"
- **Reto**: alternativa alcanzable, **ya**

## Slide 4 — La solución alcanzable
- No programar desde cero → **vibecoding** + frameworks consolidados
- Stack moderno con costo ~0:
  - FastAPI (Python) — backend en horas, no meses
  - MySQL en Docker — un comando, sin instalación
  - Tailwind CDN — UI premium consistente
  - SSE — stock tiempo real sin WebSockets ni infra extra
- **De 6 meses → días**
- Funciones completas: login con roles, reserva de stock, pago con tarjeta simulado y panel admin.

## Slide 5 — Arquitectura (servicios separados, misma API)
```
[web :8080  e-commerce]  ─┐
                          ├─ fetch /api ─> [API FastAPI :8000] ─ ORM ─> [MySQL :3306]
[admin :8081  panel]     ─┘                      └─ SSE /api/stream/stock (público)
```
- **3 servicios independientes** en `docker compose`: tienda (web), panel (admin) y API JSON. Cada uno en su propio origen, todos contra la **misma API**.
- Auth por **token Bearer** (CORS) — el panel admin está aislado del e-commerce.
- Carrito en el navegador (localStorage); el checkout manda los items a la API.
- Un solo `docker compose up -d --build` levanta todo (mysql, api, web, admin, phpMyAdmin).

## Slide 6 — Modelo de datos
- 10 tablas:
  - `tipo_producto`, `producto`
  - `sucursal` (las 6 del caso)
  - `stock_sucursal` (M:M con `existencia` + `reservado`)
  - `cliente`, `usuario` (login + rol)
  - `factura` + `detalle_factura`
  - `pago` (pasarela simulada), `reserva` (hold de stock con TTL)
- Cumple la **restricción 2** del PDF y la extiende con sucursales, usuarios, pagos y reservas.
- Diagrama ER (mostrar pizarra o screenshot phpMyAdmin).

## Slide 7 — Stock en tiempo real (Server-Sent Events)
- Problema: cliente A compra → cliente B debe ver stock actualizado **sin recargar**.
- Solución: SSE — canal HTTP unidireccional servidor→cliente.
- Al iniciar el pago, el backend:
  1. Bloquea fila con `SELECT...FOR UPDATE` (concurrencia segura).
  2. **Reserva** stock (sube `reservado`, no toca `existencia`) con TTL de 15 min.
  3. Publica evento al broker → todos ven bajar el **disponible**.
  4. Si el pago se aprueba, descuenta `existencia`; si se rechaza o expira, libera la reserva.
- Frontend: badge se actualiza con destello amarillo.

## Slide 8 — Demo en vivo
- Registro/login de cliente
- Catálogo (con filtros) → detalle con disponibilidad por sucursal
- Carrito → checkout → **reserva** (disponible baja en otra pestaña) → **pago con tarjeta** (animada) → factura PDF
- Panel admin: dashboard con métricas/gráfica, inventario, CRUD productos, pedidos, usuarios
- **Simulador de ventas** corriendo en otra terminal → stock baja en pantalla

## Slide 9 — Despliegue
- Local: `docker compose up -d` + `uvicorn`
- Demo pública: `ngrok http 8000`
- Producción real (post-emergencia): cualquier VPS, Railway, Fly.io, Render — el mismo `docker-compose.yml` funciona

## Slide 10 — Tiempo y costo
| | Propuesta original | Solución entregada |
|---|---|---|
| Tiempo | 6 meses | **Días** |
| Infra | Servidor dedicado | Docker local + ngrok (USD 0) |
| Mantenimiento | Alto | Bajo (un compose file) |

## Slide 11 — Próximos pasos
- Pasarela de pagos **real** (Stripe / Recurrente / NeoNet) — hoy está simulada con validación Luhn
- Dominio propio (`elmembrillo.com.gt`)
- Catálogo extendido con más fotos
- Notificaciones por email de la factura
- Reportes avanzados para junta directiva

## Slide 12 — Cierre
- Lección: con vibecoding + plataformas, una emergencia se resuelve en **días**, no meses.
- Pregunta al público: "¿Listos para verlo en vivo?"
- Q&A

---

## Tips de presentación
- Cronometra: 6 min slides + 3 min demo + 1 min Q&A.
- Ten ngrok abierto antes de empezar — no lo arranques en frío.
- Plan B: graba video MP4 del flujo completo por si falla la red en el aula.
- Si te preguntan "¿por qué no Shopify/WordPress?": di que sí son válidos pero el caso pide modelar BD propio (restricción 2) y SSE custom para sync tiempo real — más control y costo $0.
