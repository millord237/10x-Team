# 10x Team - Service Startup Script
# Developed by Team 10x.in

param(
    [string]$Service = "all"
)

$services = @{
    "dashboard" = @{
        "name" = "Marketing Dashboard"
        "port" = 3000
        "path" = ".claude\skills\marketing-dashboard"
        "command" = "npm run dev"
    }
    "canvas" = @{
        "name" = "TLDraw Canvas"
        "port" = 3001
        "path" = "canvas"
        "command" = "npm run dev"
    }
    "websocket" = @{
        "name" = "WebSocket Server"
        "port" = 3002
        "path" = "canvas"
        "command" = "node server.js"
    }
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  10x Team Services" -ForegroundColor Cyan
Write-Host "  Developed by Team 10x.in" -ForegroundColor Gray
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

function Start-Service($key, $config) {
    Write-Host "Starting $($config.name) on port $($config.port)..." -ForegroundColor Green
    $fullPath = Join-Path $PSScriptRoot $config.path
    Start-Process -FilePath "cmd" -ArgumentList "/c cd /d `"$fullPath`" && $($config.command)" -WindowStyle Normal
    Write-Host "  -> $($config.name) starting at http://localhost:$($config.port)" -ForegroundColor Yellow
}

if ($Service -eq "all") {
    Write-Host "Starting all services..." -ForegroundColor Magenta
    Write-Host ""
    foreach ($key in $services.Keys) {
        Start-Service $key $services[$key]
    }
} elseif ($services.ContainsKey($Service)) {
    Start-Service $Service $services[$Service]
} else {
    Write-Host "Unknown service: $Service" -ForegroundColor Red
    Write-Host "Available services: all, dashboard, canvas, websocket" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Port Assignments:" -ForegroundColor White
Write-Host "  - Marketing Dashboard: 3000" -ForegroundColor Gray
Write-Host "  - TLDraw Canvas:       3001" -ForegroundColor Gray
Write-Host "  - WebSocket Server:    3002" -ForegroundColor Gray
Write-Host "  - API Server:          3003" -ForegroundColor Gray
Write-Host "================================" -ForegroundColor Cyan
