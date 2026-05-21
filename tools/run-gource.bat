@echo off
title BlackRose Repository Visualizer (Gource)
echo =======================================================
echo     BlackRose Git Repository Visualizer via Gource     
echo =======================================================
echo.
echo Checking for Gource in path...
where gource >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Gource is not installed or not in PATH!
    echo To run this, please install Gource first:
    echo   - Via Chocolatey: choco install gource
    echo   - Via Scoop: scoop install gource
    echo   - Or download from official site: https://github.com/acaudwell/Gource
    echo.
    pause
    exit /b 1
)

echo Launching Gource visualizer in 1080p high fidelity mode...
gource ^
  -1920x1080 ^
  --background 0e1117 ^
  --glow-intensity 1.2 ^
  --glow-colour b11e3b ^
  --title "BlackRose - Evolution Timeline" ^
  --font-scale 1.5 ^
  --seconds-per-day 1.5 ^
  --auto-skip-seconds 1.0 ^
  --key ^
  --max-files 0 ^
  --hide mouse,progress ^
  --user-scale 1.5 ^
  --highlight-users ^
  --stop-at-end ^
  --file-idle-time 0 ^
  --max-file-lag -1 ^
  .

echo.
echo Evolution map animation finished successfully.
pause
