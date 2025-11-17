param(
    [switch]$Setup,
    [switch]$Serve
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venvPath = Join-Path $root ".venv"
$venvExe = Join-Path $venvPath "Scripts\python.exe"
$inner = Join-Path $root "ExpenseTracker"

function Ensure-Venv {
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    }
}

if ($Setup) {
    Ensure-Venv
    Write-Host "Upgrading pip and installing requirements..."
    & $venvExe -m pip install --upgrade pip
    & $venvExe -m pip install -r (Join-Path $inner 'vercel-requirements.txt')

    Write-Host "Initializing database (init_db.py)..."
    Push-Location $inner
    & $venvExe init_db.py
    Pop-Location

    Write-Host "Setup complete. To serve the app run: .\run.ps1 -Serve"
}

if ($Serve) {
    Write-Host "Starting Flask development server... (Ctrl+C to stop)"
    Push-Location $inner
    & $venvExe main.py
    Pop-Location
}

if (-not $Setup -and -not $Serve) {
    Write-Host "Usage: .\run.ps1 -Setup (to create venv, install deps and init DB)"
    Write-Host "       .\run.ps1 -Serve  (to start the dev server)"
}
