<# Estado del despliegue Blue-Green. Uso: ./status.ps1 #>
$ns = 'membrillo'
$color = (kubectl -n $ns get svc api -o jsonpath="{.spec.selector.color}").Trim()
Write-Host "PRODUCCION (svc api) -> color: $color" -ForegroundColor Green
Write-Host ""
Write-Host "Pods:" -ForegroundColor Cyan
kubectl -n $ns get pods -o wide
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
kubectl -n $ns get svc
