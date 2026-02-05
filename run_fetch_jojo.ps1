# ============================================
# JOJO's Bizarre Adventure Data Collection Script
# Execution: .\run_fetch_jojo.ps1
# ============================================

# Set encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  JOJO's Bizarre Adventure Data Collection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python environment
Write-Host "[1/3] Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  ✓ Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found, please install Python first" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "[2/3] Checking dependencies..." -ForegroundColor Yellow
try {
    $dependencies = @("requests", "loguru", "python-dotenv", "pycryptodome", "openpyxl")
    foreach ($dep in $dependencies) {
        $check = & python -c "import $dep" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $dep" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $dep not installed" -ForegroundColor Red
            Write-Host "  Please run: pip install -r requirements.txt" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "  ✗ Dependency check failed" -ForegroundColor Red
    exit 1
}

# Check .env configuration file
Write-Host "[3/3] Checking configuration files..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "COOKIES") {
        Write-Host "  ✓ COOKIES configured" -ForegroundColor Green
    } else {
        Write-Host "  ✗ COOKIES not configured, please log in to Xiaohongshu to get Cookie" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✗ .env file not found" -ForegroundColor Red
    Write-Host "  Please create .env file and configure COOKIES" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting to collect JOJO's Bizarre Adventure notes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Execute collection
Write-Host "📌 Search topic: JOJO's Bizarre Adventure" -ForegroundColor Magenta
Write-Host "📌 Target quantity: 100 items" -ForegroundColor Magenta
Write-Host "📌 Output file: JOJO's Bizarre Adventure.jsonl" -ForegroundColor Magenta
Write-Host ""

$ErrorActionPreference = "Continue"

# Call Python script
& python fetch_by_subject.py "JOJO's Bizarre Adventure" --quantity 100

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ Collection completed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Output files located at: datas/excel_datas/" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ Collection failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Pause to view results
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
