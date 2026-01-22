#!/bin/bash
# ============================================
# 10x Team - Linux/Mac Installation Script
# Developed by Team 10x.in
# ============================================
# This script installs all dependencies and sets up the environment
# Run: chmod +x setup.sh && ./setup.sh
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Paths
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
SETUP_LOG="$ROOT_DIR/.setup-status.json"
CANVAS_DIR="$ROOT_DIR/canvas"
DASHBOARD_DIR="$ROOT_DIR/.claude/skills/marketing-dashboard"

# Functions
print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

print_step() {
    echo -e "${YELLOW}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${GRAY}[INFO]${NC} $1"
}

# ============================================
# Start Installation
# ============================================
print_header "10x Team Installation"
echo -e "${GRAY}Developed by Team 10x.in${NC}"
echo ""

# ============================================
# Check if already installed
# ============================================
if [ -f "$SETUP_LOG" ] && [ "$1" != "--force" ]; then
    installed=$(cat "$SETUP_LOG" | grep -o '"installed": true' || echo "")
    if [ -n "$installed" ]; then
        print_info "10x Team is already installed!"
        print_info "To reinstall, run: ./setup.sh --force"
        exit 0
    fi
fi

# ============================================
# Detect OS
# ============================================
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
fi

print_info "Detected OS: $OS"

# ============================================
# 1. Check/Install Python
# ============================================
print_header "Step 1: Python Setup"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_step "Python not found. Installing Python..."

    if [ "$OS" == "macos" ]; then
        if command -v brew &> /dev/null; then
            brew install python@3.12
        else
            print_error "Homebrew not found. Please install Homebrew first:"
            print_info "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [ "$OS" == "linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3.12 python3.12-venv python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python312 python312-pip
        else
            print_error "Package manager not found. Please install Python manually."
            exit 1
        fi
    fi

    print_success "Python installed successfully"
fi

# ============================================
# 2. Check/Install Node.js
# ============================================
print_header "Step 2: Node.js Setup"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
else
    print_step "Node.js not found. Installing Node.js..."

    if [ "$OS" == "macos" ]; then
        if command -v brew &> /dev/null; then
            brew install node@20
        fi
    elif [ "$OS" == "linux" ]; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi

    print_success "Node.js installed successfully"
fi

# ============================================
# 3. Create Python Virtual Environment
# ============================================
print_header "Step 3: Python Virtual Environment"

if [ -d "$VENV_DIR" ]; then
    print_info "Virtual environment already exists at $VENV_DIR"
else
    print_step "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# Upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install Python dependencies
print_step "Installing Python dependencies..."
if [ -f "$ROOT_DIR/requirements.txt" ]; then
    pip install -r "$ROOT_DIR/requirements.txt" --quiet
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found!"
fi

# ============================================
# 4. Install Node.js Dependencies (Root)
# ============================================
print_header "Step 4: Root Node.js Dependencies"

print_step "Installing root dependencies..."
cd "$ROOT_DIR"
npm install --silent 2>/dev/null || npm install
print_success "Root dependencies installed"

# ============================================
# 5. Install Canvas (TLDraw) Dependencies
# ============================================
print_header "Step 5: Canvas (TLDraw) Setup"

if [ -d "$CANVAS_DIR" ]; then
    print_step "Installing canvas dependencies..."
    cd "$CANVAS_DIR"
    npm install --silent 2>/dev/null || npm install
    print_success "Canvas dependencies installed"
else
    print_info "Canvas directory not found, skipping..."
fi

# ============================================
# 6. Install Marketing Dashboard Dependencies
# ============================================
print_header "Step 6: Marketing Dashboard Setup"

if [ -d "$DASHBOARD_DIR" ]; then
    print_step "Installing dashboard dependencies..."
    cd "$DASHBOARD_DIR"
    npm install --silent 2>/dev/null || npm install
    print_success "Dashboard dependencies installed"

    # Install app dependencies
    if [ -d "$DASHBOARD_DIR/app" ]; then
        print_step "Installing dashboard app dependencies..."
        cd "$DASHBOARD_DIR/app"
        npm install --silent 2>/dev/null || npm install
        print_success "Dashboard app dependencies installed"
    fi
else
    print_info "Dashboard directory not found, skipping..."
fi

# ============================================
# 7. Setup Environment Files
# ============================================
print_header "Step 7: Environment Configuration"

cd "$ROOT_DIR"

# Copy .env.example to .env if not exists
if [ -f "$ROOT_DIR/.env.example" ] && [ ! -f "$ROOT_DIR/.env" ]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    print_success "Created .env from .env.example"
    print_info "Please edit .env and add your API keys"
fi

# Copy .claude/.env.example to .claude/.env if not exists
if [ -f "$ROOT_DIR/.claude/.env.example" ] && [ ! -f "$ROOT_DIR/.claude/.env" ]; then
    cp "$ROOT_DIR/.claude/.env.example" "$ROOT_DIR/.claude/.env"
    print_success "Created .claude/.env from .claude/.env.example"
fi

# ============================================
# 8. Create Output Directories
# ============================================
print_header "Step 8: Create Output Directories"

OUTPUT_DIRS=(
    "output"
    "output/workflows"
    "output/reports"
    "output/exports"
    "output/pdfs"
    "output/presentations"
    "output/logs"
)

for dir in "${OUTPUT_DIRS[@]}"; do
    mkdir -p "$ROOT_DIR/$dir"
    print_info "Created: $dir"
done
print_success "Output directories created"

# ============================================
# 9. Save Setup Status
# ============================================
print_header "Step 9: Saving Setup Status"

PYTHON_VER=$(python3 --version 2>&1)
NODE_VER=$(node --version 2>&1)
NPM_VER=$(npm --version 2>&1)

cat > "$SETUP_LOG" << EOF
{
    "installed": true,
    "installed_at": "$(date '+%Y-%m-%d %H:%M:%S')",
    "python_version": "$PYTHON_VER",
    "node_version": "$NODE_VER",
    "npm_version": "$NPM_VER",
    "venv_path": "$VENV_DIR",
    "platform": "$OS",
    "installed_by": "$USER"
}
EOF

print_success "Setup status saved to .setup-status.json"

# ============================================
# Final Summary
# ============================================
print_header "Installation Complete!"

echo ""
echo -e "  ${GREEN}10x Team has been successfully installed!${NC}"
echo ""
echo -e "  ${WHITE}Installed Components:${NC}"
echo -e "    ${GRAY}- Python: $PYTHON_VER${NC}"
echo -e "    ${GRAY}- Node.js: $NODE_VER${NC}"
echo -e "    ${GRAY}- Virtual Environment: $VENV_DIR${NC}"
echo ""
echo -e "  ${WHITE}Next Steps:${NC}"
echo -e "    ${YELLOW}1. Edit .env file and add your API keys${NC}"
echo -e "    ${YELLOW}2. Activate venv: source .venv/bin/activate${NC}"
echo -e "    ${YELLOW}3. Start Claude Code: claude${NC}"
echo ""
echo -e "  ${WHITE}Quick Start Commands:${NC}"
echo -e "    ${GRAY}- Start Dashboard:  npm run dashboard${NC}"
echo -e "    ${GRAY}- Start Canvas:     npm run canvas${NC}"
echo -e "    ${GRAY}- Start All:        npm run start:all${NC}"
echo ""
echo -e "  ${WHITE}Port Assignments:${NC}"
echo -e "    ${GRAY}- Marketing Dashboard: http://localhost:3000${NC}"
echo -e "    ${GRAY}- TLDraw Canvas:       http://localhost:3001${NC}"
echo -e "    ${GRAY}- WebSocket Server:    ws://localhost:3002${NC}"
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GRAY}  Developed by Team 10x.in${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

cd "$ROOT_DIR"
