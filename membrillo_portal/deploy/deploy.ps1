<#
  Despliega El Membrillo Portal en el cluster K8s actual (kubectl config).
  Crea el namespace, el ConfigMap de SQL inicial (schema + seed) y aplica
  todos los manifiestos. El Service de produccion arranca apuntando a BLUE.

  Uso:  ./deploy.ps1
#>
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent     # membrillo_portal/
$k8s  = "$PSScriptRoot/k8s"
$ns   = 'membrillo'

Write-Host "==> namespace + config" -ForegroundColor Cyan
kubectl apply -f "$k8s/00-namespace.yaml"
kubectl apply -f "$k8s/10-config.yaml"

Write-Host "==> ConfigMap SQL inicial (desde ../sql)" -ForegroundColor Cyan
# create+apply idempotente
kubectl -n $ns create configmap membrillo-sql --from-file="$root/sql" `
  --dry-run=client -o yaml | kubectl apply -f -

Write-Host "==> MySQL" -ForegroundColor Cyan
kubectl apply -f "$k8s/20-mysql.yaml"
kubectl -n $ns rollout status deploy/mysql --timeout=180s

Write-Host "==> API blue + green" -ForegroundColor Cyan
kubectl apply -f "$k8s/30-api-blue.yaml"
kubectl apply -f "$k8s/31-api-green.yaml"
kubectl apply -f "$k8s/32-api-service.yaml"
kubectl -n $ns rollout status deploy/api-blue --timeout=120s

Write-Host "==> Frontends web + admin" -ForegroundColor Cyan
kubectl apply -f "$k8s/40-web.yaml"
kubectl apply -f "$k8s/41-admin.yaml"
kubectl -n $ns rollout status deploy/web --timeout=120s

Write-Host ""
Write-Host "Despliegue OK." -ForegroundColor Green
Write-Host "  Tienda : http://localhost:30080"
Write-Host "  Admin  : http://localhost:30081  (admin@membrillo.gt / membrillo123)"
Write-Host "  Produccion sirve color: " -NoNewline
kubectl -n $ns get svc api -o jsonpath="{.spec.selector.color}"; Write-Host ""
