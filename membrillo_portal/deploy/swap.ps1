<#
  Blue-Green swap SIN downtime: cambia el selector 'color' del Service de
  produccion (api) entre blue y green. Valida que el destino este Ready antes.

  Uso:
    ./swap.ps1            # cambia al color contrario al actual
    ./swap.ps1 -To green  # fuerza destino
#>
param(
  [ValidateSet('blue','green')] [string]$To
)
$ErrorActionPreference = 'Stop'
$ns = 'membrillo'

$current = (kubectl -n $ns get svc api -o jsonpath="{.spec.selector.color}").Trim()
Write-Host "Produccion actual -> $current" -ForegroundColor Yellow

if (-not $To) { $To = if ($current -eq 'blue') { 'green' } else { 'blue' } }
if ($To -eq $current) { Write-Host "Ya esta en $To. Nada que hacer." -ForegroundColor Green; exit 0 }

Write-Host "==> Validando que api-$To este Ready..." -ForegroundColor Cyan
kubectl -n $ns rollout status deploy/api-$To --timeout=120s

# Smoke test contra el pod destino (service de preview siempre apunta a green;
# si vamos a blue, validamos por la salud del deployment ya confirmada arriba).
Write-Host "==> Swap del Service api: $current -> $To" -ForegroundColor Cyan
$patch = "{`"spec`":{`"selector`":{`"app`":`"api`",`"color`":`"$To`"}}}"
kubectl -n $ns patch svc api -p $patch

Write-Host ""
Write-Host "SWAP COMPLETO. Produccion ahora sirve: $To" -ForegroundColor Green
Write-Host "Recarga http://localhost:30080 y mira el footer (pod/color/version)."
Write-Host "Rollback inmediato:  ./swap.ps1 -To $current"
