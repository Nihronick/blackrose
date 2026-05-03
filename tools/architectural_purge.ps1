# BlackRose Final Architectural Purge
# This script removes loose files in the root and services directories that have been moved or deprecated.

$ErrorActionPreference = "Continue"
$ROOT = Resolve-Path "$PSScriptRoot/.."

$Targets = @(
    "$ROOT/deploy-backend.ps1",
    "$ROOT/deploy-frontend.ps1",
    "$ROOT/FINAL_CLEANUP.ps1",
    "$ROOT/backend/services/notification_service.py",
    "$ROOT/backend/services/translation_service.py",
    "$ROOT/backend/trash/",
    "$ROOT/backend/experiments/"
)

Write-Host "--- BlackRose Architectural Cleanup ---" -ForegroundColor Cyan

foreach ($Target in $Targets) {
    if (Test-Path $Target) {
        Write-Host "Deleting legacy/moved file: $Target" -ForegroundColor Yellow
        Remove-Item -Path $Target -Recurse -Force
    }
}

Write-Host "Root directory is now clean. All deployment scripts moved to /tools/." -ForegroundColor Green
