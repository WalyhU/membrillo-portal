<#
  Construye las imagenes Docker del portal El Membrillo.
  api: una sola imagen etiquetada v1 (blue) y v2 (green) -> mismo codigo,
       el color/version se inyecta por variables de entorno en K8s.

  Uso:
    ./build-images.ps1                 # solo docker build (Docker Desktop K8s)
    ./build-images.ps1 -Loader minikube
    ./build-images.ps1 -Loader kind
#>
param(
  [ValidateSet('none','minikube','kind')] [string]$Loader = 'none'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent   # membrillo_portal/

Write-Host "==> build api (v1/v2)" -ForegroundColor Cyan
docker build -t membrillo-api:v1 -f "$root/Dockerfile" "$root"
docker tag membrillo-api:v1 membrillo-api:v2

Write-Host "==> build web" -ForegroundColor Cyan
docker build -t membrillo-web:v1 -f "$root/deploy/Dockerfile.web" "$root"

Write-Host "==> build admin" -ForegroundColor Cyan
docker build -t membrillo-admin:v1 -f "$root/deploy/Dockerfile.admin" "$root"

$images = @('membrillo-api:v1','membrillo-api:v2','membrillo-web:v1','membrillo-admin:v1')

if ($Loader -eq 'minikube') {
  foreach ($i in $images) { Write-Host "==> minikube image load $i"; minikube image load $i }
} elseif ($Loader -eq 'kind') {
  foreach ($i in $images) { Write-Host "==> kind load docker-image $i"; kind load docker-image $i }
}

Write-Host "Listo. Imagenes:" -ForegroundColor Green
$images | ForEach-Object { Write-Host "  $_" }
