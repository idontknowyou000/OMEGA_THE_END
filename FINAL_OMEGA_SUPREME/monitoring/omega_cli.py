#!/usr/bin/env python3
"""
OMEGA-PLOUTUS X COMMAND LINE INTERFACE
======================================

Interactive command-line interface for OMEGA-PLOUTUS X cyber weapon system.
Allows direct interaction with the AI server and malware components.

Features:
- Real-time AI decision making
- Attack execution from all integrated repositories
- System monitoring and status
- Interactive attack selection
- Command history and logging

USAGE:
    python3 omega_cli.py                    # Interactive mode
    python3 omega_cli.py --attack kiosk     # Direct attack execution
    python3 omega_cli.py --status           # System status
    python3 omega_cli.py --help             # Show help

AUTHOR: OMEGA-PLOUTUS X Development Team
"""

import os
import sys
import time
import json
import socket
import argparse
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import cmd
try:
    import readline
except ImportError:
    # readline not available on Windows
    readline = None

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class OmegaCLI(cmd.Cmd):
    """OMEGA-PLOUTUS X Command Line Interface"""

    intro = """
🔥 OMEGA-PLOUTUS X COMMAND LINE INTERFACE 🔥
============================================

Welcome to the OMEGA-PLOUTUS X control system.
Type 'help' or '?' for available commands.

SYSTEM STATUS: INITIALIZING...
"""

    prompt = "OMEGA> "

    def __init__(self):
        super().__init__()
        self.ai_host = '127.0.0.1'
        self.ai_port = 31337
        self.ai_socket = None
        self.connected = False
        self.attack_history = []
        self.system_status = {}

        # Available attacks from integrated repositories
        self.available_attacks = {
            # Repository-based attacks
            'kiosk_evasion': 'Kiosk breakout from Kiosk-evasion-BADUsb-Bruteforce',
            'usb_hid_attack': 'USB HID exploitation from usb-hid-and-run',
            'gtfobins_exploit': 'Privilege escalation from GTFOBins.github.io',
            'av_bypass': 'Antivirus bypass from OSEP-Pre',
            'arp_poisoning': 'ARP poisoning attack - REPLACES APDU attacks',
            'financial_ml': 'Financial ML from Advances-In-Financial-Machine-Learning',
            'deep_learning': 'Deep learning attacks from awesome-deep-learning',
            'ml_complete': 'Complete ML suite from machine_learning_complete',
            'ml_guide': 'ML optimization from Machine-Learning-Guide',
            'automl': 'AutoML from mindware',
            'weka_ml': 'ML classification from zero-desktop-weka',
            'web_bruteforce': 'Web kiosk bruteforce from webkiosk-bruteforce-script',
            'synthetic_gen': 'Synthetic attacks from eclipse_synth',
            'kiosk_config': 'Kiosk config exploit from self-service-kiosk',
            'proxy_attack': 'Proxy attacks from badass_proxy_clean.py',

            # Specialized attacks
            'atm_jackpot': 'Complete ATM jackpot attack sequence',
            'crypto_wallet': 'Cryptocurrency wallet exploitation',
            'mining_attack': 'Crypto mining deployment',
            'market_manip': 'Financial market manipulation',
            'wireless_mitm': 'Wireless man-in-the-middle',
            'bluetooth_attack': 'Bluetooth exploitation',
            'network_scan': 'Comprehensive network scanning',
            'lateral_move': 'Windows lateral movement',
            'sql_attack': 'SQL Server exploitation',
            'ad_exploit': 'Active Directory attacks',
            'command_injection': 'Command injection attacks from PayloadsAllTheThings',
            'metasploit_attack': 'Metasploit Framework exploit execution',
            'scapy_network_attack': 'Scapy-enhanced network attacks (ARP, DNS, MITM)'
        }

        # Connect to AI server
        self.connect_to_ai()

    def connect_to_ai(self):
        """Connect to OMEGA AI server"""
        try:
            self.ai_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ai_socket.settimeout(5)
            self.ai_socket.connect((self.ai_host, self.ai_port))
            self.connected = True
            print("✅ Connected to OMEGA AI Server")
            self.update_status()
        except Exception as e:
            print(f"❌ Failed to connect to AI server: {e}")
            print("💡 Start the AI server with: python3 omega_ai_server.py")
            self.connected = False

    def update_status(self):
        """Update system status"""
        if not self.connected:
            self.system_status = {"status": "disconnected"}
            return

        try:
            # Send status request
            status_cmd = "STATUS:system_health_check"
            self.ai_socket.send(status_cmd.encode('utf-8'))

            response = self.ai_socket.recv(4096).decode('utf-8')
            if response:
                self.system_status = json.loads(response) if response.startswith('{') else {"raw_response": response}
            else:
                self.system_status = {"status": "no_response"}
        except Exception as e:
            self.system_status = {"error": str(e)}

    def send_attack_command(self, attack_type: str, target: str = "auto", **kwargs) -> Dict[str, Any]:
        """Send attack command to AI server"""
        if not self.connected:
            return {"error": "Not connected to AI server"}

        try:
            # Build command
            command = f"ATTACK:{attack_type}"
            if target != "auto":
                command += f",target={target}"

            # Add additional parameters
            for key, value in kwargs.items():
                command += f",{key}={value}"

            # Send command
            self.ai_socket.send(command.encode('utf-8'))

            # Get response
            response = self.ai_socket.recv(4096).decode('utf-8')

            if response:
                try:
                    result = json.loads(response)
                    self.attack_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "command": command,
                        "result": result
                    })
                    return result
                except json.JSONDecodeError:
                    return {"raw_response": response}
            else:
                return {"error": "No response from server"}

        except Exception as e:
            return {"error": str(e)}

    # Command handlers

    def do_status(self, arg):
        """Show system status"""
        self.update_status()
        print("\n🔥 OMEGA-PLOUTUS X SYSTEM STATUS")
        print("=" * 40)

        if self.connected:
            print(f"🧠 AI Server: 🟢 CONNECTED ({self.ai_host}:{self.ai_port})")
        else:
            print(f"🧠 AI Server: 🔴 DISCONNECTED ({self.ai_host}:{self.ai_port})")

        # Show attack history
        if self.attack_history:
            print(f"📊 Attack History: {len(self.attack_history)} commands executed")
            last_attack = self.attack_history[-1]
            print(f"🎯 Last Attack: {last_attack['command']} ({last_attack['timestamp']})")
        else:
            print("📊 Attack History: No attacks executed yet")

        # Show available attacks
        print(f"🎯 Available Attacks: {len(self.available_attacks)} integrated from repositories")

        print("\n" + "=" * 40)

    def do_attack(self, arg):
        """Execute attack: attack <type> [target]"""
        if not arg:
            print("❌ Usage: attack <type> [target]")
            print("💡 Use 'attacks' to list available attack types")
            return

        args = arg.split()
        attack_type = args[0]
        target = args[1] if len(args) > 1 else "auto"

        if attack_type not in self.available_attacks:
            print(f"❌ Unknown attack type: {attack_type}")
            print("💡 Use 'attacks' to list available attack types")
            return

        print(f"🚀 Executing attack: {attack_type}")
        print(f"🎯 Target: {target}")
        print(f"📝 Description: {self.available_attacks[attack_type]}")
        print("-" * 50)

        result = self.send_attack_command(attack_type, target)

        if "error" in result:
            print(f"❌ Attack failed: {result['error']}")
        else:
            print("✅ Attack executed successfully!")
            if "command" in result:
                print(f"🎯 AI Selected: {result['command']}")
            if "success_prob" in result:
                print(f"📊 Success Probability: {result['success_prob']:.1%}")
            if "reasoning" in result:
                print(f"🧠 AI Reasoning: {result['reasoning'][:100]}...")

        print("-" * 50)

    def do_attacks(self, arg):
        """List all available attack types"""
        print("\n🎯 AVAILABLE ATTACKS FROM INTEGRATED REPOSITORIES")
        print("=" * 60)

        categories = {
            "Repository-Based": ["kiosk_evasion", "usb_hid_attack", "gtfobins_exploit", "av_bypass", "arp_poisoning"],
            "Machine Learning": ["financial_ml", "deep_learning", "ml_complete", "ml_guide", "automl", "weka_ml"],
            "Specialized": ["web_bruteforce", "synthetic_gen", "kiosk_config", "proxy_attack"],
            "Compound Attacks": ["atm_jackpot", "crypto_wallet", "mining_attack", "market_manip"],
            "Network Attacks": ["wireless_mitm", "bluetooth_attack", "network_scan", "lateral_move"],
            "System Attacks": ["sql_attack", "ad_exploit", "command_injection", "metasploit_attack"]
        }

        for category, attacks in categories.items():
            print(f"\n🔥 {category}:")
            for attack in attacks:
                if attack in self.available_attacks:
                    print(f"  • {attack:15} - {self.available_attacks[attack]}")

        print("\n" + "=" * 60)
        print("💡 Usage: attack <type> [target]")
        print("💡 Example: attack kiosk_evasion localhost")

    def do_history(self, arg):
        """Show attack history"""
        if not self.attack_history:
            print("📊 No attack history available")
            return

        print("\n📊 ATTACK HISTORY")
        print("=" * 80)

        for i, entry in enumerate(self.attack_history[-10:], 1):  # Show last 10
            timestamp = entry['timestamp']
            command = entry['command']
            result = entry.get('result', {})

            status = "✅ SUCCESS" if "error" not in result else "❌ FAILED"
            print(f"{i:2d}. [{timestamp}] {status}")
            print(f"    Command: {command}")
            if "command" in result:
                print(f"    AI Decision: {result['command']}")
            print()

    def do_connect(self, arg):
        """Reconnect to AI server"""
        print("🔄 Reconnecting to AI server...")
        if self.ai_socket:
            self.ai_socket.close()
        self.connect_to_ai()

    def do_monitor(self, arg):
        """Start real-time system monitoring"""
        print("📊 Starting real-time monitoring (Ctrl+C to stop)...")
        try:
            while True:
                self.do_status("")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

    def do_ai(self, arg):
        """Send raw command to AI server"""
        if not arg:
            print("❌ Usage: ai <command>")
            return

        result = self.send_attack_command(f"RAW:{arg}")
        print(f"📡 AI Response: {result}")

    def do_help(self, arg):
        """Show help information"""
        if arg:
            # Specific command help
            super().do_help(arg)
        else:
            # General help
            print("""
🔥 OMEGA-PLOUTUS X COMMAND LINE INTERFACE 🔥
=============================================

CORE COMMANDS:
  status              - Show system status
  attacks             - List all available attacks
  attack <type> [tgt] - Execute specific attack
  history             - Show attack history
  monitor             - Real-time system monitoring

ADVANCED COMMANDS:
  connect             - Reconnect to AI server
  ai <command>        - Send raw command to AI
  help [command]      - Show help for specific command

ATTACK CATEGORIES:
  • Repository-Based  - Direct from integrated repos
  • Machine Learning  - AI-powered attacks
  • Specialized       - Unique exploit techniques
  • Compound          - Multi-vector attacks
  • Network           - Wireless and network attacks
  • System            - OS and service exploitation

EXAMPLES:
  OMEGA> status
  OMEGA> attacks
  OMEGA> attack kiosk_evasion
  OMEGA> attack atm_jackpot bank_terminal
  OMEGA> history
  OMEGA> monitor

SYSTEM INFO:
  • AI Server: localhost:31337
  • Integrated Repos: 15 repositories
  • Attack Vectors: 25+ techniques
  • Platforms: Linux, Windows

Type 'quit' or 'exit' to exit the interface.
""")

    def do_quit(self, arg):
        """Exit the CLI"""
        print("🛑 Shutting down OMEGA CLI...")
        if self.ai_socket:
            self.ai_socket.close()
        return True

    def do_exit(self, arg):
        """Exit the CLI"""
        return self.do_quit(arg)

    # Aliases
    do_q = do_quit
    do_s = do_status
    do_a = do_attacks
    do_h = do_history
    do_m = do_monitor

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="OMEGA-PLOUTUS X Command Line Interface")
    parser.add_argument("--attack", help="Execute specific attack directly")
    parser.add_argument("--target", default="auto", help="Target for attack")
    parser.add_argument("--status", action="store_true", help="Show system status and exit")
    parser.add_argument("--list-attacks", action="store_true", help="List available attacks and exit")
    parser.add_argument("--ai-host", default="127.0.0.1", help="AI server host")
    parser.add_argument("--ai-port", type=int, default=31337, help="AI server port")

    args = parser.parse_args()

    # Create CLI instance
    cli = OmegaCLI()
    cli.ai_host = args.ai_host
    cli.ai_port = args.ai_port

    # Handle direct commands
    if args.status:
        cli.do_status("")
        return

    if args.list_attacks:
        cli.do_attacks("")
        return

    if args.attack:
        cli.do_attack(f"{args.attack} {args.target}")
        return

    # Interactive mode
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        cli.do_quit("")

if __name__ == "__main__":
    main()
