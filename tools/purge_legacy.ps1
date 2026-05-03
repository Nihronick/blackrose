# BlackRose Final Directory Cleanup
# This script removes the legacy Scripts folder and other temporary artifacts.

$ErrorActionPreference = "Continue"

$Targets = @(
    "scripts/",
    "backend/trash/",
    "backend/experiments/"
)

Write-Host "--- BlackRose Final Purge ---" -ForegroundColor Cyan

foreach ($Target in $Targets) {
    if (Test-Path $Target) {
        Write-Host "Deleting legacy directory: $Target" -ForegroundColor Yellow
        Remove-Item -Path $Target -Recurse -Force
    }
}

Write-Host "Project is now clean. Useful tools moved to /tools/." -ForegroundColor Green
