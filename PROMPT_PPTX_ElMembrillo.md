# Prompt para generar la presentación PowerPoint — Portal "El Membrillo"

> Pega TODO el contenido del bloque siguiente (entre los `===`) en ChatGPT o Claude y pídele:
> *"Genera un archivo .pptx con python-pptx siguiendo exactamente esta especificación."*
>
> El prompt está auto-contenido: incluye el caso, las restricciones, el stack y el contenido literal de cada slide. La IA solo necesita producir el código `python-pptx` y el archivo final.

---

```
================================================================
PROMPT — PRESENTACIÓN PROFESIONAL "EL MEMBRILLO" (.pptx)
================================================================

ROL
Eres un consultor senior de transformación digital. Vas a generar un archivo PowerPoint (.pptx) ejecutivo de 11 slides para presentar ante la junta directiva de "Jaleas Artesanales S.A. — El Membrillo" la solución de portal e-commerce desarrollada en respuesta a la crisis de ventas por la pandemia.

ENTREGABLE
Un único script en Python usando la librería python-pptx que produzca el archivo "Presentacion_ElMembrillo.pptx". El script debe ser ejecutable de extremo a extremo (incluye todos los imports, la creación de la presentación, cada slide, todos los textos literalmente como aparecen abajo, y el guardado del archivo).

================================================================
1) CONTEXTO DEL CASO (para que internalices el problema)
================================================================
- Empresa: Jaleas Artesanales S.A., marca "El Membrillo", familia Guzmán, San Francisco El Alto, Sacatepéquez (Guatemala). Más de 40 años fabricando jaleas artesanales (estrella: Jalea de Membrillo).
- Canal de distribución: directo (restaurantes, tiendas, distribuidores) — NO se vende en supermercados grandes.
- 6 sucursales: Guatemala, Quetzaltenango, Mazatenango, Escuintla, Puerto Barrios, Jutiapa.
- Sistema heredado: Visual Basic del 2005, factura en línea por sucursal, estable pero sin presencia digital.
- Crisis: marzo 2020 — pandemia, ventas cayeron 85% en 3 meses, vendedores no pueden visitar clientes, clientes no pueden movilizarse entre departamentos.
- Junta directiva (Lic. Lorena Guzmán) exige una alternativa al "necesito 6 meses para un portal" — solución alcanzable de inmediato.

RESTRICCIONES DEL CATEDRÁTICO (deben aparecer cumplidas en la presentación):
1. NO programar el sitio desde cero — solo vibecoding, low-code o plataformas (Shopify, WooCommerce, Wix, WordPress, Tiendanube).
2. Modelar y simular el módulo de ventas con al menos: tipos de producto, productos (precios y existencias), clientes y facturación.
3. El portal debe interactuar con el modelo de datos y reflejar/actualizar el stock en tiempo real.
4. Fecha de entrega: 11 de abril de 2026.
5. Ponderación: 8 puntos de zona.

================================================================
2) SOLUCIÓN ENTREGADA — STACK Y JUSTIFICACIÓN EJECUTIVA
================================================================
Stack final (todas las decisiones deben justificarse en términos de NEGOCIO: tiempo, costo, riesgo, mantenimiento — no en jargon técnico profundo):

| Tecnología                | Función                                  | Por qué se eligió (ángulo ejecutivo)                                                                                                            |
|---------------------------|-------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| FastAPI (Python)          | Motor del portal                          | Permite llevar el portal del concepto a producción en días, no meses. Framework consolidado, documentación automática, miles de empresas lo usan. |
| MySQL 8                   | Base de datos                             | Estándar de la industria, gratuito, compatible con cualquier proveedor de hosting. Escala sin reescribir si las ventas en línea explotan.         |
| Docker / Docker Compose   | Empaquetado y despliegue                  | Toda la infraestructura levanta con un solo comando. Reduce el riesgo de fallas en demo y migración a producción a casi cero.                     |
| SQLAlchemy (ORM)          | Acceso a datos                            | Aísla la lógica de negocio de la base de datos. Si mañana migramos a PostgreSQL o a la nube, no se reescribe el código.                          |
| Jinja2 + Bootstrap CDN    | Front-end                                 | Diseño profesional inmediato sin diseñador dedicado. Responsive (funciona en celular del cliente sin trabajo extra).                              |
| Server-Sent Events (SSE)  | Stock en tiempo real                      | Cumple la restricción crítica: el inventario se actualiza en pantalla del cliente sin recargar. Más simple y barato de operar que WebSockets.    |
| ReportLab                 | Factura en PDF                            | Genera la factura descargable inmediatamente, profesional, sin servicios externos ni costos por documento.                                        |
| ngrok                     | Demo pública / piloto                     | Permite mostrar el portal desde cualquier red sin contratar hosting. Costo cero durante la fase de prueba.                                       |
| Vibecoding asistido por IA| Metodología de desarrollo                | Cumple la restricción "no programar desde cero": construcción guiada por IA sobre frameworks consolidados. Reduce tiempo de 6 meses a días.       |

Por qué NO Shopify / WooCommerce / Wix:
- Son válidos para catálogos genéricos, pero el caso EXIGE un modelo de datos propio (restricción 2) y sincronización de stock en tiempo real entre 6 sucursales (restricción 3) que esas plataformas no resuelven nativamente sin pagar planes superiores y plugins. La solución entregada da más control, costo cero y dueño total de los datos.

Modelo de datos entregado (7 tablas):
tipo_producto, producto, sucursal, stock_sucursal, cliente, factura, detalle_factura.
Cumple la restricción 2 y la extiende con sucursales y stock distribuido.

Resultados clave a destacar en la presentación:
- Tiempo: 6 meses → días.
- Costo de infraestructura para el piloto: USD 0.
- Stock en vivo entre las 6 sucursales (factor diferenciador).
- Factura PDF descargable al cierre de cada compra.
- Migración a producción: el mismo paquete corre en cualquier hosting (Railway, Fly.io, Render, VPS).

================================================================
3) ESTILO VISUAL — CORPORATIVO SOBRIO
================================================================
- Fondo: blanco (#FFFFFF) en todas las slides excepto portada y cierre.
- Portada y cierre: fondo gris muy oscuro (#1F2937) con título en blanco.
- Color de acento (titulares y barras): vino corporativo #8B0000.
- Color secundario (líneas, separadores): gris medio #6B7280.
- Color de texto principal: gris oscuro #111827.
- Tipografía: Calibri (default seguro de PowerPoint). Títulos en bold 32-36 pt, subtítulos 20 pt, cuerpo 16-18 pt, notas/footer 11 pt.
- Sin emojis. Sin imágenes decorativas innecesarias. Sin gradientes llamativos.
- Cada slide lleva en la esquina inferior izquierda el texto pequeño (11 pt, #6B7280): "El Membrillo — Jaleas Artesanales S.A.  |  Plan de Continuidad Digital"
- Y en la esquina inferior derecha, número de slide (11 pt, #6B7280): "X / 11".
- Una barra horizontal vino (#8B0000) de 4 pt debajo del título de cada slide para uniformidad.
- Todas las tablas con encabezado en fondo vino (#8B0000) y texto blanco; filas alternas en #F3F4F6.

================================================================
4) ESPECIFICACIÓN SLIDE POR SLIDE (11 SLIDES)
================================================================

SLIDE 1 — PORTADA
- Fondo #1F2937
- Título centrado (blanco, 44 pt, bold): "Plan de Continuidad Digital"
- Subtítulo (blanco, 28 pt): "Portal de Ventas en Línea — El Membrillo"
- Línea inferior (gris claro, 18 pt): "Jaleas Artesanales S.A.  ·  Junta Directiva  ·  Abril 2026"
- Pie centrado (gris claro, 14 pt): "Presentado por: Gerencia de Sistemas"

SLIDE 2 — EL PROBLEMA
- Título: "El golpe de la pandemia"
- Tres bloques horizontales (cards con borde gris claro):
  • "85%" (vino, 48 pt, bold)  →  "caída de ventas en los primeros 3 meses de pandemia"
  • "0"   (vino, 48 pt, bold)  →  "presencia digital al inicio de la crisis"
  • "6"   (vino, 48 pt, bold)  →  "sucursales aisladas por restricciones de movilidad"
- Texto inferior (16 pt): "Los vendedores no pueden visitar clientes. Los clientes no pueden movilizarse entre departamentos. El canal tradicional, durante 40 años nuestra fortaleza, hoy es el cuello de botella."

SLIDE 3 — EL RETO PLANTEADO
- Título: "El reto de la Lic. Guzmán"
- Cita destacada (cursiva, 24 pt, color #111827, dentro de un recuadro con barra vino izquierda): "Seis meses está totalmente fuera de la realidad de la empresa. Necesito una alternativa alcanzable, ya."
- Texto inferior (18 pt): "La solución debía cumplir 5 restricciones definidas y entrar en operación en cuestión de días, no de meses."
- Lista compacta (16 pt) de las 5 restricciones (numeradas tal cual en el caso): no programar desde cero · módulo de ventas modelado · interacción con el modelo y stock en tiempo real · entrega 11 abril 2026 · presentación de la solución.

SLIDE 4 — LA SOLUCIÓN PROPUESTA
- Título: "Un portal real, en días, con costo cercano a cero"
- Mensaje central (20 pt, bold): "Construimos un portal de catálogo, carrito, facturación y stock en tiempo real, sobre una plataforma propia que respeta las 5 restricciones."
- Cuatro pilares en fila (cards con número grande vino):
  1. "Catálogo" — productos, precios y existencias siempre visibles.
  2. "Carrito + Factura PDF" — checkout y comprobante instantáneo.
  3. "Stock en vivo" — las 6 sucursales sincronizadas en tiempo real.
  4. "Listo para escalar" — mismo paquete corre en hosting profesional.

SLIDE 5 — ARQUITECTURA EN UNA VISTA
- Título: "Arquitectura simple, robusta y portable"
- Diagrama horizontal (cajas con bordes vino y flechas grises):
  [Cliente Web / Móvil] → [Portal FastAPI] → [Base de Datos MySQL]
                                 ↑
                         [Stream de Stock en Vivo]
                                 ↑
                          [Acceso Público (ngrok / hosting)]
- Texto al pie (16 pt): "Toda la infraestructura se levanta con un solo comando (Docker). El mismo paquete corre en la laptop del piloto y en producción real."

SLIDE 6 — JUSTIFICACIÓN DE TECNOLOGÍAS (1/2)
- Título: "Por qué este stack — visión ejecutiva"
- Tabla (3 columnas: Tecnología | Función | Razón ejecutiva):
  • FastAPI (Python)        | Motor del portal        | Del concepto a producción en días. Framework probado por miles de empresas.
  • MySQL 8                 | Base de datos           | Estándar de industria, gratuito, portable a cualquier hosting sin reescribir.
  • Docker Compose          | Empaquetado y despliegue| Una sola instrucción levanta todo el sistema. Reduce el riesgo en demo y migración.
  • SQLAlchemy              | Acceso a datos          | Aísla el código de la base. Cambiar de motor mañana no implica reescribir.
  • Jinja2 + Bootstrap      | Interfaz visual         | Diseño profesional y responsivo desde el día uno. Sin diseñador dedicado.

SLIDE 7 — JUSTIFICACIÓN DE TECNOLOGÍAS (2/2)
- Título: "Por qué este stack — visión ejecutiva (cont.)"
- Tabla (mismas 3 columnas):
  • Server-Sent Events (SSE)| Stock en tiempo real    | Cumple la restricción crítica: el inventario se refleja al instante. Operación más simple y barata que las alternativas.
  • ReportLab               | Factura en PDF          | Comprobante profesional al cierre de cada compra, sin servicios externos ni costos por documento.
  • ngrok                   | Acceso público inmediato| Demo desde cualquier red sin contratar hosting. Cero costo durante el piloto.
  • Vibecoding asistido     | Metodología             | Cumple la restricción "no desde cero". Construcción guiada por IA sobre frameworks maduros: pasamos de 6 meses a días.
- Pie (14 pt, cursiva, gris): "Por qué no Shopify / Wix / WooCommerce: el caso exige modelo de datos propio y stock en vivo entre las 6 sucursales — control total y costo cero."

SLIDE 8 — MODELO DE DATOS
- Título: "Modelo de datos del módulo de ventas"
- Texto introductorio (16 pt): "Siete tablas que cumplen y extienden la restricción 2 del caso."
- Tabla de 2 columnas (Tabla | Propósito):
  • tipo_producto      | Catálogo de categorías (jalea, mermelada, conserva, almíbar)
  • producto           | Productos con precio y existencias
  • sucursal           | Las 6 sucursales del caso
  • stock_sucursal     | Existencias por producto y sucursal (stock distribuido)
  • cliente            | Datos del comprador
  • factura            | Encabezado de la factura
  • detalle_factura    | Productos y cantidades de cada venta
- Pie: "Toda la operación del portal se origina y termina en este modelo. Es la fuente única de verdad."

SLIDE 9 — DEMOSTRACIÓN EN VIVO
- Título: "Lo que verán hoy en pantalla"
- Lista numerada (18 pt) de 6 pasos:
  1. Catálogo público con stock visible por sucursal.
  2. Detalle del producto y disponibilidad en cada una de las 6 sucursales.
  3. Carrito de compra y selección de sucursal.
  4. Confirmación y descarga inmediata de la factura en PDF.
  5. Panel de administración para ajuste de inventario.
  6. Simulador de ventas paralelo: el stock baja en pantalla, en vivo, sin recargar.
- Pie (14 pt, cursiva): "El paso 6 es el factor diferenciador: demuestra el cumplimiento de la restricción de stock en tiempo real."

SLIDE 10 — TIEMPO, COSTO Y RIESGO
- Título: "Comparación: propuesta original vs. solución entregada"
- Tabla de 3 columnas (Criterio | Propuesta original | Solución entregada):
  • Tiempo de implementación   | 6 meses                | Días
  • Costo de infraestructura   | Servidor dedicado      | USD 0 durante el piloto
  • Mantenimiento              | Alto (equipo dedicado) | Bajo (un archivo de configuración)
  • Riesgo de retraso          | Alto                   | Bajo — todos los componentes son maduros
  • Migración a producción     | Reescritura            | Mismo paquete, cualquier hosting
- Mensaje final (20 pt, bold, vino): "Misma meta. Una fracción del tiempo. Una fracción del costo."

SLIDE 11 — CIERRE Y PRÓXIMOS PASOS
- Fondo #1F2937
- Título (blanco, 36 pt, bold): "Próximos pasos"
- Lista (blanco, 18 pt) sin viñetas decorativas:
  1. Pasarela de pagos en línea (Recurrente, NeoNet o Stripe).
  2. Dominio propio: elmembrillo.com.gt.
  3. Login para clientes recurrentes y programa de fidelidad.
  4. Reportes ejecutivos para la junta directiva.
  5. Catálogo extendido y campañas digitales.
- Frase de cierre centrada (blanco, 24 pt, cursiva): "Con disciplina y herramientas correctas, una emergencia se resuelve en días, no en meses."
- Pie: "Gracias.  ·  Preguntas y respuestas."

================================================================
5) INSTRUCCIONES TÉCNICAS PARA EL CÓDIGO
================================================================
- Usa python-pptx.
- Tamaño de slide: 13.333 x 7.5 pulgadas (16:9 widescreen).
- Crea funciones auxiliares para: (a) aplicar el footer izquierdo + número de slide, (b) aplicar la barra vino bajo el título, (c) crear cards con borde gris claro y número grande vino, (d) crear tablas con el estilo definido (encabezado vino, filas alternas #F3F4F6).
- Coloca todos los textos literalmente como aparecen arriba (no parafrasear, no resumir).
- Al final del script, guarda el archivo como "Presentacion_ElMembrillo.pptx" e imprime una línea de confirmación.
- No incluyas dependencias adicionales más allá de python-pptx.

================================================================
6) FORMATO DE TU RESPUESTA
================================================================
Devuélveme únicamente el script Python completo en un solo bloque de código, listo para ejecutar con:
    pip install python-pptx
    python generar_pptx.py

No agregues explicaciones extra antes ni después del bloque de código.

================================================================
FIN DEL PROMPT
================================================================
```

---

## Cómo usar este prompt

1. Abre ChatGPT (GPT-4/5) o Claude.
2. Copia el bloque entre los `===` de arriba (todo, desde "ROL" hasta "FIN DEL PROMPT").
3. Pégalo como mensaje y envíalo.
4. La IA devolverá un script Python.
5. Guárdalo como `generar_pptx.py`, instala la librería y ejecuta:
   ```powershell
   pip install python-pptx
   python generar_pptx.py
   ```
6. El archivo `Presentacion_ElMembrillo.pptx` quedará listo para abrir, repasar y ajustar visualmente en PowerPoint si quieres pulir detalles.

## Notas

- El prompt está optimizado para tono **ejecutivo sobrio** (junta directiva), no para un debate técnico profundo. Si más adelante el catedrático pide más detalle técnico (FastAPI vs Flask, SSE vs WebSockets, etc.), agrega una slide extra después de la 7 con esa comparación — el outline lo soporta sin romper el flujo.
- Los colores y la tipografía Calibri están elegidos para no requerir ningún recurso externo y abrir bien en cualquier instalación de PowerPoint.
- Si quieres que en lugar de pasar este prompt a otra IA yo mismo genere el `.pptx` directamente desde aquí con el skill `pptx`, dime y lo construyo de inmediato.
