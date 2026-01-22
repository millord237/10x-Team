# ============================================
# 10x Team - Windows Installation Script
# Developed by Team 10x.in
# ============================================
# This script installs all dependencies and sets up the environment
# Run: .\install.ps1
# ============================================

param(
    [switch]$SkipPython,
    [switch]$SkipNode,
    [switch]$SkipVenv,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors
function Write-Header { param($msg) Write-Host "`n========================================" -ForegroundColor Cyan; Write-Host "  $msg" -ForegroundColor Cyan; Write-Host "========================================" -ForegroundColor Cyan }
function Write-Step { param($msg) Write-Host "[STEP] $msg" -ForegroundColor Yellow }
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Gray }

# Paths
$ROOT_DIR = $PSScriptRoot
$VENV_DIR = Join-Path $ROOT_DIR ".venv"
$SETUP_LOG = Join-Path $ROOT_DIR ".setup-status.json"
$CANVAS_DIR = Join-Path $ROOT_DIR "canvas"
$DASHBOARD_DIR = Join-Path $ROOT_DIR ".claude\skills\marketing-dashboard"
$BROWSER_EXT_DIR = Join-Path $ROOT_DIR "browser-extension"

Write-Header "10x Team Installation"
Write-Host "Developed by Team 10x.in" -ForegroundColor Gray
Write-Host ""

# ============================================
# Check if already installed
# ============================================
if ((Test-Path $SETUP_LOG) -and -not $Force) {
    $status = Get-Content $SETUP_LOG | ConvertFrom-Json
    if ($status.installed -eq $true) {
        Write-Info "10x Team is already installed!"
        Write-Info "Last installed: $($status.installed_at)"
        Write-Info "To reinstall, run: .\install.ps1 -Force"
        exit 0
    }
}

# ============================================
# 1. Check/Install Python
# ============================================
Write-Header "Step 1: Python Setup"

if (-not $SkipPython) {
    $pythonVersion = $null
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Step "Python not found. Installing Python 3.12..."

        # Download Python installer
        $pythonUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
        $pythonInstaller = Join-Path $env:TEMP "python-installer.exe"

        Write-Info "Downloading Python..."
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller

        Write-Info "Installing Python (this may take a few minutes)..."
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

        Write-Success "Python installed successfully"
    }
}

# ============================================
# 2. Check/Install Node.js
# ============================================
Write-Header "Step 2: Node.js Setup"

if (-not $SkipNode) {
    $nodeVersion = $null
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js found: $nodeVersion"
    } catch {
        Write-Step "Node.js not found. Installing Node.js 20 LTS..."

        # Download Node.js installer
        $nodeUrl = "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi"
        $nodeInstaller = Join-Path $env:TEMP "node-installer.msi"

        Write-Info "Downloading Node.js..."
        Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller

        Write-Info "Installing Node.js (this may take a few minutes)..."
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", $nodeInstaller, "/quiet", "/norestart" -Wait

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

        Write-Success "Node.js installed successfully"
    }
}

# ============================================
# 3. Create Python Virtual Environment
# ============================================
Write-Header "Step 3: Python Virtual Environment"

if (-not $SkipVenv) {
    if (Test-Path $VENV_DIR) {
        Write-Info "Virtual environment already exists at $VENV_DIR"
    } else {
        Write-Step "Creating virtual environment..."
        python -m venv $VENV_DIR
        Write-Success "Virtual environment created"
    }

    # Activate virtual environment
    Write-Step "Activating virtual environment..."
    $activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
    & $activateScript
    Write-Success "Virtual environment activated"

    # Upgrade pip
    Write-Step "Upgrading pip..."
    python -m pip install --upgrade pip --quiet
    Write-Success "pip upgraded"

    # Install Python dependencies
    Write-Step "Installing Python dependencies..."
    $requirementsFile = Join-Path $ROOT_DIR "requirements.txt"
    if (Test-Path $requirementsFile) {
        pip install -r $requirementsFile --quiet
        Write-Success "Python dependencies installed"
    } else {
        Write-Error "requirements.txt not found!"
    }
}

# ============================================
# 4. Install Node.js Dependencies (Root)
# ============================================
Write-Header "Step 4: Root Node.js Dependencies"

Write-Step "Installing root dependencies..."
Set-Location $ROOT_DIR
npm install --silent 2>$null
Write-Success "Root dependencies installed"

# ============================================
# 5. Install Canvas (TLDraw) Dependencies
# ============================================
Write-Header "Step 5: Canvas (TLDraw) Setup"

if (Test-Path $CANVAS_DIR) {
    Write-Step "Installing canvas dependencies..."
    Set-Location $CANVAS_DIR
    npm install --silent 2>$null
    Write-Success "Canvas dependencies installed"
} else {
    Write-Info "Canvas directory not found, skipping..."
}

# ============================================
# 6. Install Marketing Dashboard Dependencies
# ============================================
Write-Header "Step 6: Marketing Dashboard Setup"

if (Test-Path $DASHBOARD_DIR) {
    Write-Step "Installing dashboard dependencies..."
    Set-Location $DASHBOARD_DIR
    npm install --silent 2>$null
    Write-Success "Dashboard dependencies installed"

    # Install app dependencies
    $appDir = Join-Path $DASHBOARD_DIR "app"
    if (Test-Path $appDir) {
        Write-Step "Installing dashboard app dependencies..."
        Set-Location $appDir
        npm install --silent 2>$null
        Write-Success "Dashboard app dependencies installed"
    }
} else {
    Write-Info "Dashboard directory not found, skipping..."
}

# ============================================
# 7. Setup Environment Files
# ============================================
Write-Header "Step 7: Environment Configuration"

Set-Location $ROOT_DIR

# Copy .env.example to .env if not exists
$envExample = Join-Path $ROOT_DIR ".env.example"
$envFile = Join-Path $ROOT_DIR ".env"
if ((Test-Path $envExample) -and -not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Success "Created .env from .env.example"
    Write-Info "Please edit .env and add your API keys"
}

# Copy .claude/.env.example to .claude/.env if not exists
$claudeEnvExample = Join-Path $ROOT_DIR ".claude\.env.example"
$claudeEnvFile = Join-Path $ROOT_DIR ".claude\.env"
if ((Test-Path $claudeEnvExample) -and -not (Test-Path $claudeEnvFile)) {
    Copy-Item $claudeEnvExample $claudeEnvFile
    Write-Success "Created .claude/.env from .claude/.env.example"
}

# ============================================
# 8. Create Output Directories
# ============================================
Write-Header "Step 8: Create Output Directories"

$outputDirs = @(
    "output",
    "output\workflows",
    "output\reports",
    "output\exports",
    "output\pdfs",
    "output\presentations",
    "output\logs"
)

foreach ($dir in $outputDirs) {
    $fullPath = Join-Path $ROOT_DIR $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Info "Created: $dir"
    }
}
Write-Success "Output directories created"

# ============================================
# 9. Save Setup Status
# ============================================
Write-Header "Step 9: Saving Setup Status"

$setupStatus = @{
    installed = $true
    installed_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    python_version = (python --version 2>&1).ToString()
    node_version = (node --version 2>&1).ToString()
    npm_version = (npm --version 2>&1).ToString()
    venv_path = $VENV_DIR
    platform = "windows"
    installed_by = $env:USERNAME
}

$setupStatus | ConvertTo-Json -Depth 10 | Set-Content $SETUP_LOG
Write-Success "Setup status saved to .setup-status.json"

# ============================================
# Final Summary
# ============================================
Write-Header "Installation Complete!"

Write-Host ""
Write-Host "  10x Team has been successfully installed!" -ForegroundColor Green
Write-Host ""
Write-Host "  Installed Components:" -ForegroundColor White
Write-Host "    - Python: $($setupStatus.python_version)" -ForegroundColor Gray
Write-Host "    - Node.js: $($setupStatus.node_version)" -ForegroundColor Gray
Write-Host "    - Virtual Environment: $VENV_DIR" -ForegroundColor Gray
Write-Host ""
Write-Host "  Next Steps:" -ForegroundColor White
Write-Host "    1. Edit .env file and add your API keys" -ForegroundColor Yellow
Write-Host "    2. Activate venv: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "    3. Start Claude Code: claude" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Quick Start Commands:" -ForegroundColor White
Write-Host "    - Start Dashboard:  npm run dashboard" -ForegroundColor Gray
Write-Host "    - Start Canvas:     npm run canvas" -ForegroundColor Gray
Write-Host "    - Start All:        npm run start:all" -ForegroundColor Gray
Write-Host ""
Write-Host "  Port Assignments:" -ForegroundColor White
Write-Host "    - Marketing Dashboard: http://localhost:3000" -ForegroundColor Gray
Write-Host "    - TLDraw Canvas:       http://localhost:3001" -ForegroundColor Gray
Write-Host "    - WebSocket Server:    ws://localhost:3002" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Developed by Team 10x.in" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $ROOT_DIR
