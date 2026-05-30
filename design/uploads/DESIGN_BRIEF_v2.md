# Brief de diseño v2 — Portal "El Membrillo" (para Claude Design / Stitch)

> Extiende el brief original en `stitch_design_system_implementation/el_membrillo_premium_e_commerce/DESIGN.md`.
> Reusa **el mismo design system** (no lo cambies). Aquí se agregan **pantallas nuevas** que el sistema todavía no cubre: Login, Registro, Mi cuenta, Pago con tarjeta y el nuevo layout del Panel Admin con varias páginas.
>
> Stack objetivo de implementación: **Jinja2 + Tailwind (CDN)**, Material Symbols Outlined, Chart.js para gráficas, JS vanilla para interacciones (flip de tarjeta, máscaras, toasts, confeti). Ya hay una implementación funcional en `app/templates/` que puedes tomar como punto de partida y elevar visualmente.

---

## 1. Design system (recordatorio — no modificar)

**Paleta**
- Primario vino membrillo `#8B0000`, hover `#6B0000`
- Acento dorado `#D4A574`, dorado suave `#FFE082`
- Crema fondo `#FAF6F0`, crema cards `#F5E6D3`
- Verde OK `#4CAF50`, ámbar `#FFA726`, rojo bajo `#E53935`
- Texto oscuro `#2C1810`, texto suave `#6B5B4F`

**Tipografía**: Playfair Display (display/headlines/precios), Inter (body/labels). Eyebrow = Inter uppercase tracking 0.15em.

**Forma**: cards 16px, botones/inputs 8–12px, chips full. **Sombras**: soft `0 4px 20px rgba(139,0,0,0.08)`, lift al hover.

**Microinteracciones**: botones hover scale/elevación + ripple; cards hover lift; imágenes zoom 1.05; stock badges flash amarillo 600ms al cambiar (SSE); toasts slide-in bottom-right; skeleton shimmer crema-dorado.

---

## 2. Pantallas ya cubiertas por el brief original
Catálogo · Detalle de producto · Carrito + Checkout · Factura OK · Admin Stock.
Mantener su especificación. **Ajuste nuevo transversal**: el catálogo y el detalle muestran **disponible = existencia − reservado** (no la existencia bruta). Las badges de stock reflejan lo realmente comprable y destellan vía SSE.

---

## 3. Pantallas NUEVAS a diseñar

### 3.1 Login (`/login`)
- Card centrada crema (max ~420px) sobre fondo cálido, sombra soft.
- Logo Playfair + icono frasco dorado arriba. Headline "Bienvenido".
- Campos: correo, contraseña (toggle ver/ocultar), checkbox "Recordarme".
- Botón primario vino full-width. Link "¿No tienes cuenta? Regístrate".
- Ilustración lateral opcional (frasco/jalea) en desktop, 2 columnas.
- Estado de error en tono cálido (rojo `#E53935` suave), no alarmante.

### 3.2 Registro (`/registro`)
- Misma estética que login. Campos: nombre, correo, NIT (opcional), teléfono, contraseña + confirmación.
- Validaciones inline (contraseña ≥ 6, correo válido, contraseñas coinciden) con micro-feedback.
- Botón "Crear cuenta". Link a login.

### 3.3 Mi cuenta (`/mi-cuenta`, cliente logueado)
- Encabezado con avatar/iniciales + nombre + correo.
- Sección "Mis pedidos": lista de tarjetas, cada una con #factura, fecha, sucursal, **badge de estado** (pagada=verde, pendiente=ámbar, anulada=gris), total en Playfair, acción descargar PDF (si pagada) o "Completar pago" (si pendiente).
- Empty state ilustrado si no hay pedidos.
- (Opcional) panel de datos de perfil editable.

### 3.4 Pago con tarjeta (`/pago/{id}`) — paso 3 del stepper
Stepper superior de **4 pasos**: Carrito → Datos → **Pago** → Confirmación.
- **Tarjeta de crédito visual con flip 3D**: refleja en tiempo real número (con máscara y espacios), titular, expiración y marca (Visa/Mastercard/Amex detectada por prefijo). Al enfocar el CVV, la tarjeta gira a su reverso mostrando la banda magnética y el CVV.
- Formulario: selector de método (Tarjeta / Contra entrega), número (máscara 4-4-4-4), titular (uppercase), expiración MM/AA, CVV. Atajo "usar tarjeta de prueba 4111 1111 1111 1111".
- **Contador regresivo** de la reserva (15:00) visible — refuerza el concepto de stock reservado.
- Badges de confianza: "SSL simulado", "Validación Luhn", "Pago seguro".
- Botón "Pagar Q—": al enviar muestra spinner → "Procesando…". Aprobado → éxito; rechazado → mensaje cálido y aviso de que la reserva se liberó.
- Resumen lateral: subtotal, IVA, total (dorado), sucursal de retiro.
- Estado **reserva expirada**: pantalla con icono timer, mensaje y CTA para volver al catálogo.

### 3.5 Panel Admin — layout con sidebar y varias páginas
**Sidebar persistente** (oscuro `#2C1810`, texto crema) con logo "Admin", indicador "● SSE conectado" (pulse verde) y menú:
`Dashboard · Inventario · Productos · Pedidos · Usuarios`. Item activo resaltado en vino.

- **Dashboard** (`/admin`): 4 tarjetas métricas con icono y sparkline — Ventas hoy (Q + nº facturas), Facturas pagadas, Stock total (+ reservados), Productos bajos. Debajo, **gráfica de barras** (Chart.js) de stock por sucursal. Animación: al entrar venta por SSE, notificación slide-in "Nueva venta · Sucursal · Q—" y contador count-up.
- **Inventario** (`/admin/inventario`): matriz editable producto × sucursal; celdas con color por nivel (verde/ámbar/rojo según disponible); muestra "N reserv." cuando hay reservas; **flash amarillo 600ms** + mini-toast cuando otro usuario/venta cambia el valor (SSE); guardar por celda.
- **Productos** (`/admin/productos`): tabla con CRUD; botón "Nuevo producto" abre modal (nombre, tipo, descripción, precio, imagen); editar por fila (modal); toggle activo/inactivo con badge.
- **Pedidos** (`/admin/pedidos`): tabla de facturas con filtros (estado, sucursal); badge de estado; ver detalle (`/admin/pedidos/{id}`) con líneas, datos de cliente, totales y descarga PDF.
- **Usuarios** (`/admin/usuarios`): tabla con rol (admin/cliente), cliente vinculado, estado; toggle activo.

---

## 4. Detalles extra "innecesarios pero bonitos"
Confeti membrillo al confirmar compra (pantalla 4), check verde que escala (pop-in), tarjeta de crédito con gradiente vino y contactless dorado, toasts del SSE, skeleton al cargar listas, dark mode opcional en footer, tooltips elegantes. Tono general: **e-commerce boutique premium artesanal**, cálido, no genérico.

---

## 5. Entregable esperado
HTML + Tailwind por pantalla nueva (login, registro, mi_cuenta, pago, admin/dashboard, admin/inventario, admin/productos, admin/pedidos, admin/pedido_detalle, admin/usuarios), coherentes con las 5 pantallas previas y reutilizando el config de Tailwind ya presente en los mockups Stitch.
