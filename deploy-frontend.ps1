# Frontend deployment script for GitHub Pages
# Usage: .\deploy-frontend.ps1

$ErrorActionPreference = "Stop"
Write-Host "Starting Frontend Build and Deployment to GitHub..."

# 1. Enter frontend folder and build
Push-Location frontend

Write-Host "Installing dependencies..."
npm install

Write-Host "Building project..."
npm run build

Pop-Location

# 2. Isolated Deployment
$deployDir = Join-Path $PSScriptRoot ".deploy_temp_frontend"
if (Test-Path $deployDir) { Remove-Item $deployDir -Recurse -Force }
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy built assets
Copy-Item "frontend/dist/*" $deployDir -Recurse -Force

# Deploy using gh-pages from the isolated folder
Push-Location $deployDir
git init -b gh-pages
git config user.email "deploy@blackrose.ai"
git config user.name "BlackRose Deployer"

git remote add origin https://github.com/Nihronick/blackrose.git
git add .
git commit -m "Deploy: Clean frontend build"

Write-Host "Pushing to GitHub Pages (Force)..."
git push origin gh-pages --force

Pop-Location

# 3. Cleanup
Remove-Item $deployDir -Recurse -Force

Write-Host "Frontend deployment finished successfully!"
