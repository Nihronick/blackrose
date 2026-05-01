# Backend deployment script for Hugging Face Spaces (Docker)
# Isolated preparation strategy
# Usage: .\deploy-backend.ps1

$ErrorActionPreference = "Stop"
Write-Host "Starting Isolated Backend Deployment to Hugging Face..."

$deployDir = Join-Path $PSScriptRoot ".deploy_temp_backend"

# 1. Cleanup old deploy dir
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}

# 2. Create clean structure
New-Item -ItemType Directory -Path $deployDir | Out-Null

# 3. Copy only backend files
Write-Host "Copying backend files..."
Copy-Item "backend/*" $deployDir -Recurse -Force

# 4. Deploy from isolated folder
Push-Location $deployDir

git init -b main
git config user.email "deploy@blackrose.ai"
git config user.name "BlackRose Deployer"

$hfToken = $env:HF_TOKEN
if ($hfToken) {
    Write-Host "Using HF_TOKEN for authentication..."
    $remoteUrl = "https://Nihronick:$($hfToken)@huggingface.co/spaces/Nihronick/blackrose-backend"
} else {
    Write-Host "Warning: HF_TOKEN not set. Git may prompt for credentials."
    $remoteUrl = "https://huggingface.co/spaces/Nihronick/blackrose-backend"
}

git remote add origin $remoteUrl
git add .
git commit -m "Deploy: Clean backend build"

Write-Host "Pushing to Hugging Face (Force)..."
git push origin main --force

Pop-Location

# 5. Final Cleanup
Remove-Item $deployDir -Recurse -Force

Write-Host "Backend deployment finished successfully!"
