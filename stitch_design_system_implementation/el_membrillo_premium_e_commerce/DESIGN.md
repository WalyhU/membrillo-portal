---
name: El Membrillo - Premium E-commerce
colors:
  surface: '#fff8f6'
  surface-dim: '#efd4d0'
  surface-bright: '#fff8f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff0ee'
  surface-container: '#ffe9e6'
  surface-container-high: '#fee2dd'
  surface-container-highest: '#f8dcd8'
  on-surface: '#261816'
  on-surface-variant: '#5a403c'
  inverse-surface: '#3d2c2a'
  inverse-on-surface: '#ffedea'
  outline: '#8e706b'
  outline-variant: '#e3beb8'
  surface-tint: '#b52619'
  primary: '#610000'
  on-primary: '#ffffff'
  primary-container: '#8b0000'
  on-primary-container: '#ff907f'
  inverse-primary: '#ffb4a8'
  secondary: '#7c572d'
  on-secondary: '#ffffff'
  secondary-container: '#fecb97'
  on-secondary-container: '#79542a'
  tertiary: '#00178d'
  on-tertiary: '#ffffff'
  tertiary-container: '#0025c8'
  on-tertiary-container: '#9ea9ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad4'
  primary-fixed-dim: '#ffb4a8'
  on-primary-fixed: '#410000'
  on-primary-fixed-variant: '#920703'
  secondary-fixed: '#ffdcbc'
  secondary-fixed-dim: '#efbd8a'
  on-secondary-fixed: '#2c1700'
  on-secondary-fixed-variant: '#614018'
  tertiary-fixed: '#dfe0ff'
  tertiary-fixed-dim: '#bcc3ff'
  on-tertiary-fixed: '#000d60'
  on-tertiary-fixed-variant: '#0d2ccc'
  background: '#fff8f6'
  on-background: '#261816'
  surface-variant: '#f8dcd8'
  primary-hover: '#6B0000'
  bg-cream: '#FAF6F0'
  card-cream: '#F5E6D3'
  success-green: '#4CAF50'
  warning-amber: '#FFA726'
  error-red: '#E53935'
  text-dark: '#2C1810'
  text-muted: '#6B5B4F'
typography:
  display-hero:
    fontFamily: Playfair Display
    fontSize: 64px
    fontWeight: '700'
    lineHeight: '1.1'
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Playfair Display
    fontSize: 22px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  eyebrow:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.15em
  price-lg:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

Diseña un portal e-commerce premium para "El Membrillo - Jaleas Artesanales S.A.", marca familiar guatemalteca fundada en 1962, con 6 sucursales (Guatemala, Quetzaltenango, Mazatenango, Escuintla, Puerto Barrios, Jutiapa). Estética cálida, artesanal-elegante, rural-premium tipo "farm-to-table" boutique. Web desktop + responsive mobile.

═══════════════════════════════════
DESIGN SYSTEM
═══════════════════════════════════
Paleta:
- Primario vino membrillo: #8B0000
- Primario hover: #6B0000
- Acento dorado: #D4A574
- Crema fondo: #FAF6F0
- Crema cards: #F5E6D3
- Verde stock OK: #4CAF50
- Ámbar stock medio: #FFA726
- Rojo stock bajo: #E53935
- Texto oscuro: #2C1810
- Texto suave: #6B5B4F

Tipografía:
- Headlines: Playfair Display (serif elegante)
- Body: Inter
- Labels/eyebrow: Inter uppercase tracking 0.15em
- Precios: Playfair Display bold

Forma: bordes redondeados 12px en cards, 8px en botones, full en chips.

Sombras: soft layered (0 4px 20px rgba(139,0,0,0.08)).

Microinteracciones globales:
- Botones: hover scale(1.02) + sombra elevada, active scale(0.98), ripple effect al click
- Cards: hover lift 4px + glow vino sutil
- Imágenes: zoom 1.05 al hover con transición 400ms ease
- Stock badges: pulse cuando cambian (flash amarillo 600ms)
- Toast notifications: slide-in desde bottom-right + bounce sutil
- Loading: skeleton shimmer crema-dorado

═══════════════════════════════════
PANTALLA 1 — CATÁLOGO (home)
═══════════════════════════════════
Navbar fija translúcida con backdrop-blur:
- Logo "El Membrillo" en Playfair con icono frasco dorado
- Links: Catálogo · Sucursales · Nuestra historia · Contacto
- Search bar con icono lupa, placeholder "Busca tu jalea favorita..."
- Icono carrito con badge contador rojo que hace bounce + pulse al agregar item
- Toggle "Stock en vivo" con dot verde latiendo

Hero full-width:
- Fondo degradado vino #8B0000 → #C9302C con overlay textura sutil de hojas
- Headline Playfair 64px: "Sabor que cuenta historias"
- Subtítulo: "Jaleas artesanales hechas a mano en Guatemala desde 1962"
- CTA primario "Ver catálogo" botón crema con flecha animada hover
- Badge flotante esquina: "● Stock en vivo · 6 sucursales conectadas" con dot verde pulse
- Mockup decorativo de 3 frascos de jalea con etiquetas elegantes

Sección filtros sticky bajo navbar:
- Chips redondeados por tipo: Todos / Jaleas / Mermeladas / Conservas / Almíbares (activo en vino)
- Slider de precio Q15-Q80 con tooltips
- Dropdown sucursal
- Chip toggle "Solo con stock" con dot verde
- Botón "Limpiar filtros" link sutil

Grid productos 4 columnas (3 tablet, 2 mobile):
- Card crema con bordes 12px
- Imagen frasco centrada con fondo degradado pastel suave
- Badge esquina superior izquierda según estado: "Más vendido" dorado / "Nuevo" verde / "Pocas unidades" ámbar / "Agotado" gris
- Tipo de producto en label uppercase tracking ancho color suave
- Nombre en Playfair 22px
- Precio Q grande en Playfair bold con guion decorativo bajo
- Mini-tabla de stock por sucursal: 6 dots de color con tooltip "Sucursal: 47 unidades"
- Botón "Agregar al carrito" full-width vino con icono +, hover lift + ripple, click anima a un check verde 600ms y luego vuelve
- Animación al agregar: el icono carrito del navbar hace bounce + el badge contador incrementa con flip

Sección "Stock en tiempo real" dashboard:
- Título Playfair "Inventario vivo en las 6 sucursales"
- 6 cards mini de sucursal con: nombre, dirección corta, total unidades, barra progreso con animación stagger al cargar, indicador "● live" pulse, mini contador "12 ventas hoy"

Sección "Nuestra historia":
- Layout 2 columnas: imagen sepia familia Guzmán + texto Playfair
- Timeline horizontal: 1962 fundación → 1985 sucursal Quetzaltenango → 2010 expansión → 2020 portal digital

Footer cálido oscuro #2C1810:
- Logo + tagline
- Mapa de Guatemala con 6 pins de sucursales (hover muestra info)
- Columnas: Tienda / Sucursales / Empresa / Contacto
- Newsletter con input + botón dorado
- Redes sociales con hover scale
- Copyright "Hecho con cariño en Guatemala"

═══════════════════════════════════
PANTALLA 2 — DETALLE DE PRODUCTO
═══════════════════════════════════
Layout 2 columnas:
Columna izquierda:
- Galería con imagen principal grande del frasco + 4 thumbnails (frasco, etiqueta, ingredientes, lifestyle)
- Zoom on hover con magnifier
- Badge flotante "Receta familiar 1962"

Columna derecha:
- Breadcrumb: Inicio › Jaleas › Jalea de Membrillo
- Tipo eyebrow uppercase
- Nombre Playfair 36px
- Rating 5 estrellas + "(127 reseñas)"
- Precio Q grande con precio anterior tachado opcional
- Descripción cálida 3 líneas
- Tabla "Disponibilidad por sucursal": 6 filas con nombre sucursal + barra stock con color + número exacto + "Ver mapa"
- Selector cantidad con botones - / + animados
- Selector sucursal de retiro: cards radio con dirección
- Botón principal "Agregar al carrito" full-width vino grande con animación al click: el botón se transforma en spinner 400ms → check verde → texto "¡Agregado!" → vuelve. Simultáneo: toast bottom-right "✓ Jalea de Membrillo agregada al carrito" con miniatura del producto y botón "Ver carrito"
- Botón secundario "Comprar ahora" outline dorado
- Acordeones: Ingredientes / Maridajes recomendados / Información nutricional / Envío

Sección "Te puede gustar":
- Carrusel de 4 productos relacionados con scroll snap

Sección reseñas con cards de clientes y rating

═══════════════════════════════════
PANTALLA 3 — CARRITO + CHECKOUT
═══════════════════════════════════
Layout 2 columnas (carrito + sidebar resumen):

Lista de items:
- Cada item card con imagen, nombre, tipo, precio unitario, selector cantidad - / + (animado), subtotal, botón eliminar con animación slide-out + fade
- Empty state ilustrado: frasco vacío grande + "Tu carrito está esperando" + CTA "Explorar catálogo"

Sidebar sticky resumen:
- "Resumen de compra" título Playfair
- Lista subtotales por producto
- Subtotal
- IVA 12%
- Envío "Gratis en sucursal"
- Total grande dorado
- Form checkout: nombre, NIT, email, teléfono, sucursal de retiro (cards radio), notas opcional
- Botón "Confirmar y generar factura" full-width vino con icono lock, hover lift, click → spinner → "Procesando..." → success
- Badges confianza: "Pago seguro" / "Factura electrónica" / "Stock garantizado"
- Métodos de pago iconos

Stepper superior 3 pasos: Carrito → Datos → Confirmación

═══════════════════════════════════
PANTALLA 4 — FACTURA OK (éxito)
═══════════════════════════════════
Layout centrado:
- Animación check verde grande 100px con círculo expandiendo
- Headline Playfair "¡Gracias por tu compra!"
- Subtítulo "Tu factura #000123 está lista"
- Card resumen con: número factura, fecha, sucursal de retiro, items mini-lista, total
- Botón principal "Descargar factura PDF" vino con icono download
- Botón secundario "Volver al catálogo" outline
- Sección "¿Qué sigue?": pasos 1-2-3 timeline (Recibirás email → Retira en sucursal → Disfruta)
- Confeti sutil en colores marca al cargar la página
- Mapa con pin de la sucursal de retiro + "Cómo llegar"

═══════════════════════════════════
PANTALLA 5 — ADMIN STOCK
═══════════════════════════════════
Layout dashboard con sidebar izquierda:
Sidebar:
- Logo Membrillo Admin
- Menu: Dashboard / Productos / Stock / Pedidos / Sucursales / Reportes
- Indicador "● SSE conectado" pulse verde

Main:
- Header con título "Gestión de inventario" + filtros sucursal + botón "Sincronizar" con spinner animado
- Cards top métricas: Total productos / Stock total / Ventas hoy / Productos bajos (con sparkline)
- Matriz editable tipo spreadsheet:
  - Filas: 7 productos con miniatura
  - Columnas: 6 sucursales
  - Celdas con número editable inline
  - Color de fondo según nivel: verde / ámbar / rojo
  - Cuando otro usuario cambia un valor (SSE): la celda hace flash amarillo 600ms con animación pulse y muestra mini-toast "Actualizado por otro usuario"
- Botón "Guardar cambios" sticky bottom-right con contador "3 cambios pendientes"
- Tabla de últimos movimientos con scroll virtual
- Gráfica de barras stock por sucursal (Chart.js style)

Animación hero del admin: cuando entra una venta nueva por SSE, una notificación slide-in top con "Nueva venta · Sucursal Quetzaltenango · Q45.00" + el contador de ventas día incrementa con count-up animado.

═══════════════════════════════════
DETALLES UX/UI EXTRA (sí, "innecesarios pero bonitos")
═══════════════════════════════════
- Cursor custom con dot dorado en hover sobre productos
- Parallax sutil en hero
- Scroll smooth con offset navbar
- Page transitions fade entre rutas
- Dark mode toggle en footer (paleta vino oscuro + crema)
- Micro-iluminación dorada al hover en cards de producto (efecto spotlight siguiendo cursor)
- Breadcrumbs con animación de tinta dibujándose
- Badges con bordes animados estilo "shimmer" en productos destacados
- Imágenes lazy loading con blur-up placeholder
- Tooltips elegantes con flecha y delay 300ms
- Modal de "agregado al carrito" estilo drawer lateral derecho con slide-in suave + lista actualizada del carrito + CTAs "Seguir comprando" y "Ir a checkout"
- Confetti membrillo al completar primera compra
- Loading skeleton con shimmer dorado sobre crema
- Empty states ilustrados (no genéricos)
- Error states con tono cálido, no alarmante

Genera las 5 pantallas con todas estas especificaciones. Estilo final: e-commerce boutique premium, no genérico.