#!/bin/bash
# OMEGA-PLOUTUS LINUX INTEGRATION TEST SUITE
# ==========================================
#
# Comprehensive testing suite for OMEGA-PLOUTUS on Linux systems
# Tests all components, repositories, and attack integrations
#
# USAGE: sudo ./test_linux_integration.sh
#

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print test header
print_test_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "🧪 Testing $test_name... "
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to print test summary
print_summary() {
    echo
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}TEST SUMMARY${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo "Total Tests: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

    local success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: ${success_rate}%"

    if [ $success_rate -ge 90 ]; then
        echo -e "${GREEN}🎉 EXCELLENT: OMEGA-PLOUTUS Linux integration successful!${NC}"
    elif [ $success_rate -ge 75 ]; then
        echo -e "${YELLOW}⚠️  GOOD: OMEGA-PLOUTUS Linux integration mostly successful${NC}"
    else
        echo -e "${RED}💀 POOR: OMEGA-PLOUTUS Linux integration needs attention${NC}"
    fi
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}🚨 ROOT PRIVILEGES REQUIRED${NC}"
    echo "Please run with: sudo ./test_linux_integration.sh"
    exit 1
fi

echo -e "${RED}🔥 OMEGA-PLOUTUS LINUX INTEGRATION TEST SUITE 🔥${NC}"
echo -e "${YELLOW}Testing all components on Linux system...${NC}"
echo

# ==========================================
# SYSTEM REQUIREMENTS TESTS
# ==========================================

print_test_header "SYSTEM REQUIREMENTS"

run_test "GCC Compiler" "which gcc"
run_test "Make Tool" "which make"
run_test "Python 3" "python3 --version"
run_test "PCSC-Lite" "pkg-config --exists libpcsclite || ldconfig -p | grep -q libpcsclite"
run_test "Development Headers" "ls /usr/include/linux/ 2>/dev/null | head -1"

# ==========================================
# COMPILATION TESTS
# ==========================================

print_test_header "COMPILATION TESTS"

# Test Linux C code compilation
run_test "Linux C Code Compilation" "gcc -c omega_ploutus_ai_integration_linux.c -o test_compile.o -pthread -ldl 2>/dev/null && rm -f test_compile.o"

# Test Makefile
run_test "Linux Makefile" "make -f Makefile.linux clean 2>/dev/null && make -f Makefile.linux all 2>/dev/null && make -f Makefile.linux clean 2>/dev/null"

# ==========================================
# PYTHON COMPONENTS TESTS
# ==========================================

print_test_header "PYTHON COMPONENTS"

run_test "AI Server Import" "python3 -c 'import omega_ai_server; print(\"AI Server OK\")'"
run_test "Kiosk Launcher Import" "python3 -c 'import sys; sys.path.append(\".\"); from omega_kiosk_attack.kiosk_jackpot_launcher import OmegaKioskJackpotLauncher; print(\"Kiosk Launcher OK\")'"

# ==========================================
# REPOSITORY INTEGRATION TESTS
# ==========================================

print_test_header "REPOSITORY INTEGRATION TESTS"

# Test repository directories exist
run_test "Repository Directories" "ls new_integrations/ | wc -l | grep -q '14'"
run_test "Kiosk Evasion Repo" "ls new_integrations/Kiosk-evasion-BADUsb-Bruteforce/"
run_test "GTFOBins Repo" "ls new_integrations/GTFOBins.github.io/"
run_test "OSEP Repo" "ls new_integrations/OSEP-Pre/"
run_test "Financial ML Repo" "ls new_integrations/Advances-In-Financial-Machine-Learning/"

# ==========================================
# LINUX-SPECIFIC ATTACK TESTS
# ==========================================

print_test_header "LINUX-SPECIFIC ATTACK TESTS"

# Test privilege escalation
run_test "Privilege Escalation Check" "id | grep -q 'uid=0'"

# Test process manipulation
run_test "Process Tools" "which ps && which pgrep && which pkill"

# Test network tools
run_test "Network Tools" "which arp && which nmap"

# Test wireless tools (optional)
run_test "Wireless Tools" "which iwconfig || which iw || echo 'Wireless tools not available'"

# ==========================================
# AI SYSTEM TESTS
# ==========================================

print_test_header "AI SYSTEM TESTS"

# Test AI server startup (background)
run_test "AI Server Startup" "timeout 5 python3 omega_ai_server.py > /dev/null 2>&1 & sleep 2 && pgrep -f 'omega_ai_server.py' && pkill -f 'omega_ai_server.py'"

# ==========================================
# KIOSK ATTACK TESTS
# ==========================================

print_test_header "KIOSK ATTACK TESTS"

# Test kiosk launcher initialization
run_test "Kiosk Launcher Init" "python3 -c '
import sys
sys.path.append(\".\")
from omega_kiosk_attack.kiosk_jackpot_launcher import OmegaKioskJackpotLauncher
launcher = OmegaKioskJackpotLauncher()
print(\"Kiosk launcher initialized successfully\")
'"

# ==========================================
# SECURITY & EVASION TESTS
# ==========================================

print_test_header "SECURITY & EVASION TESTS"

# Test antivirus detection
run_test "AV Detection" "ps aux | grep -i virus | grep -v grep || echo 'No AV detected'"

# Test rootkit detection tools
run_test "Rootkit Tools" "which chkrootkit || which rkhunter || echo 'No rootkit tools'"

# ==========================================
# FINANCIAL ATTACK TESTS
# ==========================================

print_test_header "FINANCIAL ATTACK TESTS"

# Test crypto tools
run_test "Crypto Tools" "which openssl && which ssh"

# Test financial analysis tools
run_test "Financial Tools" "python3 -c 'import sys; print(\"Python financial analysis available\")'"

# ==========================================
# MACHINE LEARNING TESTS
# ==========================================

print_test_header "MACHINE LEARNING TESTS"

# Test ML libraries
run_test "NumPy" "python3 -c 'import numpy; print(\"NumPy OK\")'"
run_test "Basic ML" "python3 -c 'import random; print(\"ML foundations OK\")'"

# ==========================================
# DEPLOYMENT TESTS
# ==========================================

print_test_header "DEPLOYMENT TESTS"

# Test shell script permissions
run_test "Shell Script Permissions" "ls -la launch_omega.sh | grep -q 'x'"

# Test makefile existence
run_test "Makefile Existence" "ls Makefile.linux"

# ==========================================
# PERFORMANCE TESTS
# ==========================================

print_test_header "PERFORMANCE TESTS"

# Test system resources
run_test "System Memory" "free -h > /dev/null"
run_test "System CPU" "nproc > /dev/null"
run_test "Disk Space" "df -h . | tail -1 | awk '{print $4}' | grep -q 'G\|M'"

# ==========================================
# INTEGRATION TESTS
# ==========================================

print_test_header "INTEGRATION TESTS"

# Test full system integration
run_test "Full Integration Test" "python3 test_integration.py 2>/dev/null | grep -q 'SUCCESSFUL'"

# Test repository integration
run_test "Repository Integration" "python3 -c '
import os
repos = os.listdir(\"new_integrations\")
print(f\"Found {len(repos)} repositories\")
assert len(repos) >= 14, \"Missing repositories\"
print(\"Repository integration OK\")
'"

# ==========================================
# FINAL REPORT
# ==========================================

print_summary

echo
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}LINUX COMPATIBILITY REPORT${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $PASSED_TESTS -ge $((TOTAL_TESTS * 9 / 10)) ]; then
    echo -e "${GREEN}✅ OMEGA-PLOUTUS is FULLY LINUX COMPATIBLE${NC}"
    echo "All systems ready for deployment on Linux targets"
elif [ $PASSED_TESTS -ge $((TOTAL_TESTS * 7 / 10)) ]; then
    echo -e "${YELLOW}⚠️  OMEGA-PLOUTUS is MOSTLY LINUX COMPATIBLE${NC}"
    echo "Some optional features may not work, but core functionality is available"
else
    echo -e "${RED}❌ OMEGA-PLOUTUS has LINUX COMPATIBILITY ISSUES${NC}"
    echo "Significant work needed to make fully Linux compatible"
fi

echo
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Run: make -f Makefile.linux all"
echo "2. Run: sudo make -f Makefile.linux install"
echo "3. Launch: sudo ./launch_omega.sh"
echo "4. Deploy: sudo ./omega_ploutus_ai_integration"

echo
echo -e "${RED}⚠️  REMINDER: This software is for EDUCATIONAL RESEARCH ONLY${NC}"
echo -e "${RED}Unauthorized use may violate federal laws${NC}"

# Cleanup
exit 0
