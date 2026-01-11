#!/bin/bash
# OMEGA_X Installation Script
# Automated setup for OMEGA_X Cyber Exploitation Framework

set -e

echo "🔥 OMEGA_X Installation Script 🔥"
echo "=================================="

# Check if running as root/sudo
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should NOT be run as root for security reasons"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "📍 Detected OS: $OS"

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv omega_x_env
source omega_x_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing basic dependencies..."
    pip install scapy requests cryptography paramiko psutil colorama
fi

# Install system dependencies
echo "🔧 Installing system dependencies..."

if [[ "$OS" == "linux" ]]; then
    if command -v apt &> /dev/null; then
        echo "📦 Using apt package manager..."
        sudo apt update
        sudo apt install -y python3-dev build-essential libssl-dev libffi-dev curl wget git
    elif command -v dnf &> /dev/null; then
        echo "📦 Using dnf package manager..."
        sudo dnf install -y python3-devel openssl-devel libffi-devel curl wget git
    elif command -v yum &> /dev/null; then
        echo "📦 Using yum package manager..."
        sudo yum install -y python3-devel openssl-devel libffi-devel curl wget git
    fi
elif [[ "$OS" == "macos" ]]; then
    if command -v brew &> /dev/null; then
        echo "📦 Using Homebrew..."
        brew install python3 openssl git
    else
        echo "⚠️  Homebrew not found. Please install system dependencies manually."
    fi
fi

# Build C/C++ components if CMakeLists.txt exists
if [[ -f "CMakeLists.txt" ]]; then
    echo "🔨 Building C/C++ components..."
    mkdir -p build
    cd build
    cmake ..
    make -j$(nproc)
    cd ..
fi

# Set up configuration
echo "⚙️  Setting up configuration..."
if [[ ! -f "omega_x_config.json" ]]; then
    echo "⚠️  omega_x_config.json not found, but that's okay - using defaults"
fi

# Make scripts executable
echo "🔑 Making scripts executable..."
chmod +x *.sh 2>/dev/null || true
chmod +x attacks/*.py 2>/dev/null || true
chmod +x *.py 2>/dev/null || true

# Create desktop shortcut (optional)
if [[ "$OS" == "linux" ]] && [[ -n "$DISPLAY" ]]; then
    echo "🖥️  Creating desktop shortcut..."
    cat > ~/Desktop/OMEGA_X.desktop << EOF
[Desktop Entry]
Name=OMEGA_X
Comment=Ultimate AI-Driven Cyber Exploitation Framework
Exec=$(pwd)/omega_launcher.py
Icon=$(pwd)/icon.png
Terminal=true
Type=Application
Categories=Utility;Security;
EOF
    chmod +x ~/Desktop/OMEGA_X.desktop
fi

echo ""
echo "🎉 OMEGA_X Installation Complete!"
echo "=================================="
echo ""
echo "🚀 To start OMEGA_X:"
echo "   cd $(pwd)"
echo "   source omega_x_env/bin/activate"
echo "   python3 omega_launcher.py"
echo ""
echo "📚 Available commands:"
echo "   python3 omega_launcher.py --help    # Show help"
echo "   python3 omega_launcher.py --module 0 # Full system assault"
echo ""
echo "🔧 Deployment:"
echo "   python3 attacks/deploy_malware.py --help"
echo ""
echo "⚠️  REMEMBER: Use OMEGA_X responsibly and legally!"
echo "   This is a powerful cyber exploitation framework."
echo ""
echo "🔥 OMEGA_X is now ready for deployment! 🔥"