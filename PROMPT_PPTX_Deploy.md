# Prompt para generar la presentación PowerPoint — Proyecto Final (Deploy + Kubernetes + CI/CD + Blue-Green)

> Pega TODO el contenido del bloque siguiente (entre los `===`) en ChatGPT o Claude y pídele:
> *"Genera un archivo .pptx con python-pptx siguiendo exactamente esta especificación."*
>
> El prompt está auto-contenido. El protagonista es el **proceso moderno de Ingeniería de Software**: contenedores, Kubernetes, CI/CD y deployment Blue-Green. El portal "El Membrillo" aparece solo como la aplicación que se despliega — NO es el centro de la presentación.

---

```
================================================================
PROMPT — PRESENTACIÓN PROYECTO FINAL ING. DE SOFTWARE (.pptx)
Tema central: DEPLOYMENT, KUBERNETES, CI/CD y BLUE-GREEN
================================================================

ROL
Eres un ingeniero DevOps presentando ante un catedrático y compañeros el proyecto final de Ingeniería de Software. El objetivo del proyecto NO es el tamaño del sistema, sino DEMOSTRAR COMPRENSIÓN DEL CICLO MODERNO DE DESARROLLO: análisis, desarrollo, control de versiones, automatización (CI/CD), deployment y trabajo colaborativo. La aplicación de ejemplo es un portal e-commerce ("El Membrillo"), pero la presentación se centra en CÓMO se construye, integra y despliega, no en el negocio del portal.

ENTREGABLE
Un único script en Python usando python-pptx que produzca el archivo "Presentacion_ProyectoFinal_Deploy.pptx". El script debe ser ejecutable de extremo a extremo: incluye todos los imports, la creación de la presentación, cada slide con TODOS los textos literalmente como aparecen abajo, los diagramas como cajas/flechas, y el guardado del archivo.

================================================================
1) CONTEXTO MÍNIMO (para que internalices el proyecto)
================================================================
- App de ejemplo: portal e-commerce "El Membrillo" (catálogo, login, carrito, factura, stock en vivo).
- Stack de la app (mencionar breve, NO profundizar): Backend FastAPI (Python) + MySQL 8 + API JSON; Frontends estáticos (nginx) para tienda y admin; tiempo real con Server-Sent Events.
- Requisitos mínimos del curso que la app cumple: login/autenticación, persistencia en base de datos, API funcional, frontend funcional. (Una sola slide para esto — es el "qué", no el "cómo".)
- LO IMPORTANTE (núcleo de la presentación):
  * Git y trabajo colaborativo: ramas main / develop / pruebas / feature/*, commits pequeños y descriptivos, guía para que cada integrante (y agentes IA) contribuya sin romper nada.
  * CI/CD con GitHub Actions: en cada push/PR compila el backend y construye 3 imágenes Docker.
  * Contenerización con Docker: API, frontend web y frontend admin, cada uno como imagen.
  * Orquestación con Kubernetes (local: Docker Desktop / minikube / kind).
  * Deployment Blue-Green sin downtime: dos versiones (blue v1 / green v2) conviviendo, swap de tráfico cambiando el selector de un Service.
  * Observabilidad de la demo: cada pod expone su identidad (nombre de pod, color, versión) y el footer del portal la muestra en vivo — al hacer swap se VE qué versión sirve producción.

================================================================
2) HECHOS TÉCNICOS EXACTOS (usar tal cual; no inventar)
================================================================
GIT / RAMAS:
- main      -> producción, no se toca directo.
- develop   -> integración; de aquí nacen las features.
- pruebas   -> experimentos.
- feature/tarea-1, feature/tarea-2, feature/tarea-3 -> trabajo por integrante.
- Commits Conventional: tipo(feat/fix/docs/style/refactor/test/chore): descripción corta.
- Documento "AGENTE_COMMITS.md": reglas de commits pequeños (1 cambio = 1 commit) y flujo de PR hacia develop, pensado para que hasta un modelo IA simple contribuya bien.

CI/CD (GitHub Actions, archivo .github/workflows/ci.yml):
- Se dispara en push y pull_request sobre main / develop / feature/*.
- Job 1 "backend-check": instala dependencias Python y compila el código (compileall) para garantizar que la app no tiene errores de sintaxis.
- Job 2 "docker-build" (depende del 1): construye 3 imágenes Docker — API, Web (nginx), Admin (nginx) — usando cache de GitHub Actions. No publica (push:false); valida que todo compila y empaqueta.
- Evidencias del curso: captura del pipeline en verde, archivo YAML, logs de ejecución.

DOCKER (3 imágenes):
- membrillo-api  : FastAPI con uvicorn, expone puerto 8000.
- membrillo-web  : nginx sirve la tienda estática + hace proxy de /api y /static hacia el Service de la API (mismo origen, sin CORS).
- membrillo-admin: nginx sirve el panel admin con el mismo proxy.

KUBERNETES (namespace "membrillo"):
- MySQL: Deployment + Service + PersistentVolumeClaim (1Gi, datos persistentes). El schema y los datos semilla se cargan al iniciar desde un ConfigMap (scripts SQL).
- API: DOS Deployments simultáneos:
    api-blue  -> imagen v1, variables APP_COLOR=blue,  APP_VERSION=1.0, 2 réplicas.
    api-green -> imagen v2, variables APP_COLOR=green, APP_VERSION=2.0, 2 réplicas.
  Cada pod recibe su nombre vía Downward API (variable POD_NAME = metadata.name).
- Service "api" (PRODUCCIÓN): selector { app: api, color: blue }. El valor de "color" decide a qué versión va el tráfico. EL SWAP CAMBIA ESTE SELECTOR -> Blue-Green.
- Service "api-green-preview" (PRE-PRODUCCIÓN): selector color=green, fijo, para validar la versión nueva ANTES del swap (vía kubectl port-forward).
- Frontends: Deployments web y admin, expuestos por Service tipo NodePort:
    tienda -> http://localhost:30080
    admin  -> http://localhost:30081
- Probes: readiness/liveness con HTTP GET a /api/health en la API.

ETIQUETA DE POD (clave para la demo):
- La API expone GET /api/info que devuelve { pod, color, version }.
- El footer de la tienda llama a /api/info y muestra: "pod: api-blue-xxxx · BLUE · v1.0".
- Al hacer swap, recargar la tienda muestra "pod: api-green-xxxx · GREEN · v2.0". Prueba visual de que producción cambió de versión SIN downtime.

BLUE-GREEN — MECÁNICA Y COMANDOS:
- Estado inicial: Service api -> blue (producción).
- Validar green (pre-prod): kubectl -n membrillo port-forward svc/api-green-preview 8090:8000  ->  http://localhost:8090/api/info muestra green/v2.0.
- Swap (sin downtime): se cambia el selector del Service api de color=blue a color=green (patch). Las conexiones nuevas van a green; las viejas terminan en blue.
- Script swap.ps1: detecta el color actual, valida que el destino esté Ready (rollout status) y aplica el patch. Rollback = swap de vuelta a blue (instantáneo).
- Por qué sin downtime: nunca se apaga blue antes de levantar y validar green; el cambio es solo de enrutamiento a nivel de Service.

SCRIPTS (PowerShell, en carpeta deploy/):
- build-images.ps1 : construye las imágenes (api v1/v2, web, admin); opción de cargarlas a minikube/kind.
- deploy.ps1       : crea namespace, ConfigMap SQL, MySQL, API blue+green, Services y frontends. Producción arranca en blue.
- swap.ps1         : Blue-Green swap sin downtime (con validación).
- status.ps1       : muestra a qué color apunta producción + pods + services.

================================================================
3) ESTILO VISUAL — TÉCNICO MODERNO Y SOBRIO
================================================================
- Fondo: blanco (#FFFFFF) en todas las slides excepto portada y cierre.
- Portada y cierre: fondo gris azulado muy oscuro (#0F172A) con texto blanco.
- Acento principal (titulares y barras): azul #2563EB.
- Acentos Blue-Green: azul #2563EB y verde #16A34A (usarlos para representar las versiones blue y green).
- Color secundario (líneas, separadores): gris #64748B.
- Texto principal: gris muy oscuro #0F172A.
- Tipografía: Calibri (default seguro). Títulos bold 32-36 pt, subtítulos 20 pt, cuerpo 16-18 pt, código/monospace 14 pt (usar fuente Consolas para bloques de comandos), footer 11 pt.
- Sin emojis. Diagramas con cajas rectangulares de borde de color y flechas grises.
- Cada slide: footer inferior izquierdo (11 pt, #64748B): "Proyecto Final — Ingeniería de Software  |  Deployment & Kubernetes". Inferior derecho: número de slide "X / 14".
- Barra horizontal azul (#2563EB) de 4 pt bajo el título de cada slide.
- Tablas: encabezado fondo azul #2563EB texto blanco; filas alternas #F1F5F9.
- Para representar BLUE usar relleno/borde #2563EB; para GREEN usar #16A34A.

================================================================
4) ESPECIFICACIÓN SLIDE POR SLIDE (14 SLIDES)
================================================================

SLIDE 1 — PORTADA
- Fondo #0F172A.
- Título centrado (blanco, 42 pt, bold): "Del código a producción"
- Subtítulo (blanco, 26 pt): "CI/CD, Kubernetes y Deployment Blue-Green"
- Línea (gris claro, 18 pt): "Proyecto Final — Ingeniería de Software  ·  2026"
- Pie centrado (gris claro, 14 pt): "App de ejemplo: portal El Membrillo  ·  El foco es el proceso, no el sistema"

SLIDE 2 — OBJETIVO DE LA PRESENTACIÓN
- Título: "Lo que vamos a demostrar"
- Texto (20 pt, bold): "El objetivo no es el tamaño del sistema, sino comprender el ciclo moderno de desarrollo de software."
- Lista (18 pt), seis ítems con número azul:
  1. Análisis y desarrollo de una app funcional.
  2. Control de versiones y trabajo colaborativo con Git.
  3. Automatización con un pipeline CI/CD.
  4. Contenerización con Docker.
  5. Orquestación con Kubernetes.
  6. Deployment Blue-Green sin downtime.
- Pie (14 pt, cursiva, gris): "La aplicación es el vehículo; el proceso es el destino."

SLIDE 3 — LA APP EN UNA SLIDE (CONTEXTO)
- Título: "La aplicación que vamos a desplegar"
- Texto (16 pt): "Portal e-commerce 'El Membrillo'. Lo mencionamos rápido porque hoy importa CÓMO se despliega, no qué vende."
- Cuatro cards (requisitos mínimos cumplidos), número/ícono azul:
  • "Login / Auth" — autenticación de clientes y administradores.
  • "Base de datos" — persistencia en MySQL 8.
  • "API funcional" — API JSON con FastAPI.
  • "Frontend" — tienda y panel admin web.
- Pie (14 pt, gris): "Backend FastAPI · MySQL · Frontends nginx · stock en tiempo real (SSE)."

SLIDE 4 — GIT Y TRABAJO COLABORATIVO
- Título: "Control de versiones y colaboración"
- Diagrama de ramas (de izquierda a derecha, cajas con flechas):
  [main]  <--  [develop]  <--  [feature/tarea-1 / -2 / -3]
                   ^
               [pruebas]
- Tabla (2 columnas: Rama | Rol):
  • main            | Producción. No se toca directo.
  • develop         | Integración. De aquí nacen las features.
  • pruebas         | Experimentos sin riesgo.
  • feature/tarea-N | Trabajo de cada integrante.
- Texto (16 pt): "Commits pequeños y descriptivos (Conventional Commits). Cada cambio entra a develop por Pull Request."
- Pie (14 pt, cursiva, gris): "Guía 'AGENTE_COMMITS.md': reglas para que cada integrante —incluso con apoyo de IA— haga commits pequeños sin romper nada."

SLIDE 5 — PIPELINE CI/CD
- Título: "Integración continua con GitHub Actions"
- Diagrama horizontal (cajas borde azul, flechas grises):
  [git push / PR] -> [backend-check: instala deps + compila] -> [docker-build: 3 imágenes] -> [pipeline verde]
- Texto (16 pt): "Se ejecuta en cada push y pull request sobre main, develop y feature/*. Si algo no compila o una imagen no se construye, el pipeline falla y el equipo se entera de inmediato."
- Lista (16 pt): "Evidencias: captura del pipeline en verde · archivo ci.yml · logs de ejecución."

SLIDE 6 — CONTENEDORES (DOCKER)
- Título: "Empaquetado: tres imágenes Docker"
- Tres cards (borde azul):
  1. "membrillo-api" — FastAPI + uvicorn, puerto 8000.
  2. "membrillo-web" — nginx: tienda estática + proxy /api y /static.
  3. "membrillo-admin" — nginx: panel admin + mismo proxy.
- Texto (16 pt): "Cada componente viaja en su propia imagen. La misma imagen corre igual en la laptop, en CI y en el clúster: 'funciona en mi máquina' deja de ser excusa."

SLIDE 7 — POR QUÉ KUBERNETES
- Título: "Por qué orquestar con Kubernetes"
- Cuatro puntos (18 pt), bullet azul:
  • Réplicas y auto-recuperación: si un pod cae, K8s lo reemplaza.
  • Services: una dirección estable enruta a varios pods.
  • Escalado declarativo: cambiar 'replicas' y listo.
  • Despliegues controlados: base para Blue-Green sin downtime.
- Pie (14 pt, gris): "Clúster local: Docker Desktop / minikube / kind. El mismo manifiesto sirve para la nube."

SLIDE 8 — ARQUITECTURA EN KUBERNETES
- Título: "Arquitectura en el clúster (namespace: membrillo)"
- Diagrama (cajas y flechas). Pintar api-blue en AZUL #2563EB y api-green en VERDE #16A34A:
   [Navegador] --30080--> [web (nginx) x2] --proxy /api--> [Service: api]
   [Navegador] --30081--> [admin (nginx)]  --proxy /api--> [Service: api]
                                                 |  selector color = blue|green  (SWAP)
                               +-----------------+------------------+
                               v                                    v
                        [api-blue v1 x2]                     [api-green v2 x2]
                               +-----------------+------------------+
                                                 v
                                         [Service: mysql]
                                                 v
                                     [MySQL + PVC (1Gi)  /  init SQL por ConfigMap]
- Pie (14 pt, gris): "El Service 'api' es el interruptor del Blue-Green. 'api-green-preview' (no mostrado) permite validar green antes del swap."

SLIDE 9 — LA ETIQUETA DEL POD
- Título: "Cada pod dice quién es"
- Texto (16 pt): "La API expone GET /api/info -> { pod, color, version }. El footer de la tienda lo muestra en vivo."
- Recuadro monospace (Consolas 14 pt, fondo #F1F5F9):
  GET /api/info
  { "pod": "api-blue-7c9d…", "color": "blue", "version": "1.0" }
- Recuadro tipo footer (mostrar el texto que ve el usuario, 18 pt):
  "pod: api-blue-7c9d… · BLUE · v1.0"
- Pie (14 pt, cursiva, gris): "Esta etiqueta es la prueba visual del swap: al cambiar producción de blue a green, el footer cambia solo."

SLIDE 10 — QUÉ ES BLUE-GREEN
- Título: "Deployment Blue-Green: cero downtime"
- Texto (18 pt): "Dos entornos idénticos conviven. BLUE atiende producción mientras GREEN recibe la versión nueva. Cuando GREEN está validado, se redirige el tráfico de golpe. Si algo falla, se vuelve a BLUE al instante."
- Dos cards lado a lado:
  • Card AZUL (borde #2563EB): "BLUE — v1.0 — Producción actual"
  • Card VERDE (borde #16A34A): "GREEN — v2.0 — Nueva versión en espera"
- Pie (14 pt, gris): "Ventaja vs. despliegue tradicional: no hay ventana de mantenimiento ni usuarios viendo errores durante la actualización."

SLIDE 11 — CÓMO FUNCIONA EL SWAP
- Título: "El swap es un cambio de enrutamiento"
- Texto (16 pt): "El Service 'api' tiene un selector con la etiqueta 'color'. Cambiar ese valor reenvía el tráfico a la otra versión. No se reinicia nada, no se apaga blue antes de tiempo."
- Antes / Después (dos filas):
  ANTES:   Service api  ->  selector color = blue   ->  api-blue (v1.0)
  DESPUÉS: Service api  ->  selector color = green  ->  api-green (v2.0)
- Recuadro monospace (Consolas 14 pt, fondo #F1F5F9):
  # validar green antes del swap
  kubectl -n membrillo port-forward svc/api-green-preview 8090:8000
  # swap sin downtime
  ./swap.ps1            # blue -> green
  ./swap.ps1 -To blue   # rollback instantáneo

SLIDE 12 — DEMOSTRACIÓN EN VIVO
- Título: "Demo: Blue-Green en vivo"
- Lista numerada (18 pt):
  1. Ambiente actual: ./status.ps1 muestra producción = BLUE. La tienda en :30080 muestra "BLUE · v1.0".  (captura ANTES)
  2. Validar green: port-forward a api-green-preview -> /api/info devuelve "green · v2.0".  (captura STAGING/GREEN)
  3. Swap: ./swap.ps1 cambia el Service de blue a green, sin downtime.  (logs del swap)
  4. Resultado: recargar la tienda; el footer ahora muestra "GREEN · v2.0".  (captura DESPUÉS)
  5. Rollback: ./swap.ps1 -To blue regresa producción en segundos.
- Pie (14 pt, cursiva, gris): "Las 4 capturas (antes / green / swap / después) son las evidencias obligatorias de Blue-Green."

SLIDE 13 — RESUMEN DEL FLUJO
- Título: "El ciclo completo, de punta a punta"
- Diagrama horizontal (cajas borde azul, flechas grises):
  [Código + Git] -> [Pull Request a develop] -> [CI: build + imágenes] -> [Deploy a Kubernetes] -> [Blue-Green swap] -> [Producción sin downtime]
- Texto (16 pt): "Análisis, desarrollo, control de versiones, automatización, deployment y colaboración — el ciclo moderno completo en un solo proyecto."

SLIDE 14 — CIERRE
- Fondo #0F172A.
- Título (blanco, 36 pt, bold): "Conclusión"
- Lista (blanco, 18 pt):
  1. Entregamos no solo una app, sino un proceso reproducible para llevarla a producción.
  2. CI/CD detecta errores temprano y automatiza el empaquetado.
  3. Kubernetes da réplicas, recuperación y despliegues controlados.
  4. Blue-Green actualiza producción sin downtime y con rollback inmediato.
- Frase de cierre centrada (blanco, 24 pt, cursiva): "El valor no está en el tamaño del sistema, sino en la disciplina del proceso."
- Pie: "Gracias.  ·  Preguntas y respuestas."

================================================================
5) INSTRUCCIONES TÉCNICAS PARA EL CÓDIGO
================================================================
- Usa python-pptx.
- Tamaño de slide: 13.333 x 7.5 pulgadas (16:9 widescreen).
- Crea funciones auxiliares para: (a) footer izquierdo + número de slide, (b) barra azul bajo el título, (c) cards con borde de color y título grande, (d) tablas con estilo definido (encabezado azul, filas alternas #F1F5F9), (e) cajas de diagrama con flechas, (f) bloques de código monospace (Consolas, fondo #F1F5F9).
- Para los elementos BLUE usar color #2563EB; para GREEN usar #16A34A.
- Coloca todos los textos literalmente como aparecen arriba (no parafrasear, no resumir).
- Los diagramas pueden representarse con autoshapes rectangulares + conectores/flechas; si es complejo, usar cajas de texto alineadas y flechas simples.
- Al final del script guarda el archivo como "Presentacion_ProyectoFinal_Deploy.pptx" e imprime una línea de confirmación.
- No incluyas dependencias adicionales más allá de python-pptx.

================================================================
6) FORMATO DE TU RESPUESTA
================================================================
Devuélveme únicamente el script Python completo en un solo bloque de código, listo para ejecutar con:
    pip install python-pptx
    python generar_pptx_deploy.py
No agregues explicaciones extra antes ni después del bloque de código.

================================================================
FIN DEL PROMPT
================================================================
```

---

## Cómo usar este prompt

1. Abre ChatGPT o Claude.
2. Copia el bloque entre los `===` de arriba (desde "ROL" hasta "FIN DEL PROMPT").
3. Pégalo y envíalo.
4. La IA devuelve un script Python.
5. Guárdalo como `generar_pptx_deploy.py` y ejecuta:
   ```powershell
   pip install python-pptx
   python generar_pptx_deploy.py
   ```
6. Abre `Presentacion_ProyectoFinal_Deploy.pptx`, repasa y pule en PowerPoint si querés.

## Notas

- Protagonista = el proceso (CI/CD, Docker, Kubernetes, Blue-Green). El portal El Membrillo ocupa solo 1-2 slides de contexto.
- Mapea con la rúbrica del PDF (Presentación Final): Introducción/Objetivo (slides 1-2), Desarrollo (slide 3-6), Git (slide 4), CI/CD (slide 5), Blue-Green con demo en vivo (slides 10-12).
- Los datos técnicos del bloque 2 son reales de este repo: ramas, ci.yml, manifiestos K8s, /api/info, scripts deploy.ps1/swap.ps1/status.ps1. Si cambian, actualiza ese bloque antes de regenerar.
- Si preferís que yo genere el `.pptx` directamente desde aquí en vez de pasar el prompt a otra IA, decímelo.
