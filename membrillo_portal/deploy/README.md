# Despliegue — El Membrillo Portal (Kubernetes + Blue-Green)

Deployment del portal sobre **Kubernetes local** (Docker Desktop / minikube / kind)
con estrategia **Blue-Green sin downtime**. Cubre Fase 4 del proyecto final.

## Arquitectura en el cluster

```
                   NodePort 30080                 NodePort 30081
                        │                               │
                  ┌─────▼─────┐                   ┌──────▼─────┐
                  │  web (x2) │                   │ admin (x1) │   nginx: sirve estaticos
                  │   nginx   │                   │   nginx    │   + proxy /api y /static
                  └─────┬─────┘                   └──────┬─────┘
                        └──────────────┬─────────────────┘
                                       │  proxy_pass /api
                              ┌────────▼─────────┐
                              │   Service: api   │  selector color=blue|green  ◄── SWAP
                              └───┬──────────┬───┘
                       color=blue │          │ color=green
                          ┌───────▼──┐   ┌───▼────────┐
                          │ api-blue │   │ api-green  │   FastAPI (POD_NAME, COLOR, VERSION)
                          │  v1 (x2) │   │  v2 (x2)   │
                          └─────┬────┘   └─────┬──────┘
                                └──────┬───────┘
                              ┌────────▼────────┐
                              │ Service: mysql  │ ──► Deployment mysql + PVC (1Gi)
                              └─────────────────┘     init: schema + seed (ConfigMap)
```

El **footer de la tienda** llama a `/api/info` y muestra `pod · COLOR · vVERSION`.
Al hacer swap, el pod que responde cambia → se ve en vivo qué versión sirve producción.

## Requisitos

- Docker Desktop con Kubernetes habilitado **o** minikube/kind.
- `kubectl` apuntando al cluster correcto (`kubectl config current-context`).

## 1. Construir imágenes

```powershell
cd membrillo_portal/deploy
./build-images.ps1                  # Docker Desktop K8s (comparte el daemon)
# ./build-images.ps1 -Loader minikube   # si usas minikube
# ./build-images.ps1 -Loader kind        # si usas kind
```

Genera: `membrillo-api:v1`, `membrillo-api:v2`, `membrillo-web:v1`, `membrillo-admin:v1`.
(`v1`/`v2` de la API son la misma imagen; el color y versión se inyectan por env.)

## 2. Desplegar

```powershell
./deploy.ps1
```

Crea namespace `membrillo`, el `ConfigMap` de SQL (schema + seed), MySQL con PVC,
API blue+green y los frontends. Producción arranca en **BLUE**.

- Tienda: http://localhost:30080
- Admin:  http://localhost:30081  (`admin@membrillo.gt` / `membrillo123`)

> minikube: si los NodePort no abren en localhost, usa `minikube service web -n membrillo`.

## 3. Demo Blue-Green (evidencias del proyecto)

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 1. Ambiente actual | `./status.ps1` → producción = **blue**. Abrir tienda, footer muestra `pod: api-blue-… · BLUE · v1.0` | captura **antes del swap** |
| 2. Validar green | `kubectl -n membrillo port-forward svc/api-green-preview 8090:8000` y abrir http://localhost:8090/api/info → `color: green, version: 2.0` | captura **staging/green** |
| 3. Swap | `./swap.ps1` (blue→green, sin downtime) | logs del swap |
| 4. Resultado | recargar tienda, footer ahora `… · GREEN · v2.0`; `./status.ps1` confirma | captura **después del swap** |
| 5. Rollback | `./swap.ps1 -To blue` (instantáneo) | — |

El swap solo cambia el selector del Service: las conexiones nuevas van al color
destino y las viejas terminan en el anterior → **cero downtime**.

## Limpiar

```powershell
kubectl delete namespace membrillo
```

## Uso de IA

Generado con asistencia de **Claude (Claude Code)**: endpoint `/api/info` + footer del
pod, Dockerfiles de los frontends nginx, manifiestos de Kubernetes, scripts de
build/deploy/swap y el pipeline de GitHub Actions. La lógica de negocio del portal
(FastAPI, modelo de datos, SSE, pagos) es del equipo.
