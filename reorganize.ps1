# Project Reorganization Script
# Run this to move files to the new structure

Write-Host "Reorganizing College Buddy project structure..." -ForegroundColor Cyan

# Create __init__.py files
Write-Host ""
Write-Host "Creating __init__.py files..." -ForegroundColor Yellow
New-Item -Path "core/__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "tests/__init__.py" -ItemType File -Force | Out-Null
Write-Host "  Done"

# Move utility files to core/
Write-Host ""
Write-Host "Moving utility files to core/..." -ForegroundColor Yellow
if (Test-Path "response_cache.py") {
    Move-Item "response_cache.py" "core/cache.py" -Force
    Write-Host "  Moved response_cache.py -> core/cache.py"
}
if (Test-Path "analytics_logger.py") {
    Move-Item "analytics_logger.py" "core/analytics.py" -Force
    Write-Host "  Moved analytics_logger.py -> core/analytics.py"
}
if (Test-Path "background_analytics.py") {
    Move-Item "background_analytics.py" "core/background_analytics.py" -Force
    Write-Host "  Moved background_analytics.py -> core/"
}
if (Test-Path "feedback_collector.py") {
    Move-Item "feedback_collector.py" "core/feedback.py" -Force
    Write-Host "  Moved feedback_collector.py -> core/feedback.py"
}
if (Test-Path "typo_corrector.py") {
    Move-Item "typo_corrector.py" "core/typo_corrector.py" -Force
    Write-Host "  Moved typo_corrector.py -> core/"
}

# Move data files
Write-Host ""
Write-Host "Moving data files..." -ForegroundColor Yellow
if (Test-Path "response_cache.json") {
    Move-Item "response_cache.json" "data/cache/" -Force
    Write-Host "  Moved response_cache.json -> data/cache/"
}
if (Test-Path "analytics_data.json") {
    Move-Item "analytics_data.json" "data/analytics/" -Force
    Write-Host "  Moved analytics_data.json -> data/analytics/"
}
if (Test-Path "background_analytics.json") {
    Move-Item "background_analytics.json" "data/analytics/" -Force
    Write-Host "  Moved background_analytics.json -> data/analytics/"
}
if (Test-Path "scraped_data.json") {
    Move-Item "scraped_data.json" "data/scraped/" -Force
    Write-Host "  Moved scraped_data.json -> data/scraped/"
}
if (Test-Path "structured_links.csv") {
    Move-Item "structured_links.csv" "data/links/" -Force
    Write-Host "  Moved structured_links.csv -> data/links/"
}

# Move scripts
Write-Host ""
Write-Host "Moving scripts..." -ForegroundColor Yellow
if (Test-Path "preprocess_student_data.py") {
    Move-Item "preprocess_student_data.py" "scripts/" -Force
    Write-Host "  Moved preprocess_student_data.py -> scripts/"
}
if (Test-Path "start_server.bat") {
    Move-Item "start_server.bat" "scripts/" -Force
    Write-Host "  Moved start_server.bat -> scripts/"
}

# Move config files
Write-Host ""
Write-Host "Moving config files..." -ForegroundColor Yellow
if (Test-Path "render.yaml") {
    Move-Item "render.yaml" "config/" -Force
    Write-Host "  Moved render.yaml -> config/"
}
if (Test-Path "runtime.txt") {
    Move-Item "runtime.txt" "config/" -Force
    Write-Host "  Moved runtime.txt -> config/"
}
if (Test-Path ".env.example") {
    Copy-Item ".env.example" "config/" -Force
    Write-Host "  Copied .env.example -> config/"
}

# Move docs
Write-Host ""
Write-Host "Moving documentation..." -ForegroundColor Yellow
if (Test-Path "OLLAMA_SETUP.md") {
    Move-Item "OLLAMA_SETUP.md" "docs/" -Force
    Write-Host "  Moved OLLAMA_SETUP.md -> docs/"
}
if (Test-Path "PRODUCTION_RECOMMENDATIONS.md") {
    Move-Item "PRODUCTION_RECOMMENDATIONS.md" "docs/" -Force
    Write-Host "  Moved PRODUCTION_RECOMMENDATIONS.md -> docs/"
}
if (Test-Path "QUICK_START.md") {
    Move-Item "QUICK_START.md" "docs/" -Force
    Write-Host "  Moved QUICK_START.md -> docs/"
}

# Rename Student data to data/student
Write-Host ""
Write-Host "Renaming Student data folder..." -ForegroundColor Yellow
if (Test-Path "Student data") {
    Move-Item "Student data" "data/student" -Force
    Write-Host "  Renamed Student data -> data/student"
}

# Clean up duplicate venv
Write-Host ""
Write-Host "Checking for duplicate venv..." -ForegroundColor Yellow
if ((Test-Path "venv") -and (Test-Path ".venv")) {
    Write-Host "  WARNING: Found both venv and .venv folders"
    Write-Host "  Please manually remove the one you are not using"
}

Write-Host ""
Write-Host "Reorganization complete!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Update import paths in your code!" -ForegroundColor Red
Write-Host "  Old: from response_cache import ..." -ForegroundColor Gray
Write-Host "  New: from core.cache import ..." -ForegroundColor Green
Write-Host ""
Write-Host "  Old: from analytics_logger import ..." -ForegroundColor Gray
Write-Host "  New: from core.analytics import ..." -ForegroundColor Green
Write-Host ""
Write-Host "  Run: python scripts/update_imports.py (to auto-fix)" -ForegroundColor Cyan
