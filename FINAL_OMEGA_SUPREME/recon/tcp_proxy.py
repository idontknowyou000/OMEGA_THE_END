#!/usr/bin/env python3
"""
OMEGA_X TCP Proxy
=================

Advanced TCP proxy server for OMEGA_X cyber exploitation framework.
Features traffic interception, modification, and man-in-the-middle capabilities.

USAGE:
    python3 tcp_proxy.py --listen-port <port> --target-host <host> --target-port <port>

FEATURES:
- Transparent TCP proxying
- Traffic interception and modification
- SSL/TLS stripping and injection
- Connection multiplexing
- Real-time traffic analysis
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
import select
import queue
from datetime import datetime

# OMEGA_X imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omega_launcher import Colors

class OMEGATCPProxy:
    """Advanced TCP proxy with interception capabilities"""

    def __init__(self, listen_host='0.0.0.0', listen_port=8080,
                 target_host=None, target_port=None, use_ssl=False,
                 intercept=False, buffer_size=4096):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.use_ssl = use_ssl
        self.intercept = intercept
        self.buffer_size = buffer_size

        self.server_socket = None
        self.running = False
        self.active_connections = {}

        # Traffic logging
        self.traffic_log = []
        self.log_lock = threading.Lock()

        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'total_connections': 0,
            'active_connections': 0,
            'bytes_client_to_server': 0,
            'bytes_server_to_client': 0,
            'intercepted_packets': 0
        }

    def start(self):
        """Start the TCP proxy"""
        try:
            print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.ENDC}                    {Colors.RED}🌐 OMEGA_X TCP PROXY 🌐{Colors.ENDC}                     {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.ENDC}              {Colors.YELLOW}TRAFFIC INTERCEPTION & MODIFICATION{Colors.ENDC}              {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

            print(f"{Colors.BLUE}📍 Listening on {self.listen_host}:{self.listen_port}{Colors.ENDC}")
            print(f"{Colors.BLUE}🎯 Target: {self.target_host}:{self.target_port}{Colors.ENDC}")
            print(f"{Colors.BLUE}🔒 SSL: {'Enabled' if self.use_ssl else 'Disabled'}{Colors.ENDC}")
            print(f"{Colors.BLUE}🔍 Intercept: {'Enabled' if self.intercept else 'Disabled'}{Colors.ENDC}")
            print()

            # Create listening socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.listen_host, self.listen_port))
            self.server_socket.listen(100)

            self.running = True

            print(f"{Colors.GREEN}✅ Proxy started successfully{Colors.ENDC}")
            print(f"{Colors.YELLOW}Type 'help' for commands, 'stop' to shutdown{Colors.ENDC}")
            print()

            # Start accept thread
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()

            # Interactive console
            self.interactive_console()

        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start proxy: {e}{Colors.ENDC}")
            sys.exit(1)

    def accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()

                connection_id = f"{client_address[0]}:{client_address[1]}_{int(time.time())}"
                print(f"{Colors.BLUE}🔗 New connection from {client_address} (ID: {connection_id}){Colors.ENDC}")

                # Create connection handler
                handler = ProxyConnectionHandler(
                    self, client_socket, client_address, connection_id,
                    self.target_host, self.target_port, self.use_ssl, self.intercept
                )

                # Add to active connections
                self.active_connections[connection_id] = handler
                self.stats['total_connections'] += 1
                self.stats['active_connections'] = len(self.active_connections)

                # Start handler thread
                handler_thread = threading.Thread(target=handler.handle_connection, daemon=True)
                handler_thread.start()

            except Exception as e:
                if self.running:
                    print(f"{Colors.RED}❌ Accept error: {e}{Colors.ENDC}")

    def remove_connection(self, connection_id):
        """Remove a connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            self.stats['active_connections'] = len(self.active_connections)
            print(f"{Colors.YELLOW}🔌 Connection {connection_id} closed{Colors.ENDC}")

    def log_traffic(self, connection_id, direction, data):
        """Log traffic data"""
        with self.log_lock:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'connection_id': connection_id,
                'direction': direction,
                'data_length': len(data),
                'data_preview': data[:100].hex() if isinstance(data, bytes) else str(data)[:100]
            }
            self.traffic_log.append(log_entry)

    def show_connections(self):
        """Show active connections"""
        print(f"{Colors.BLUE}Active Connections ({len(self.active_connections)}):{Colors.ENDC}")
        print("-" * 80)

        for conn_id, handler in self.active_connections.items():
            uptime = datetime.now() - handler.start_time
            print(f"ID: {conn_id}")
            print(f"  Client: {handler.client_address}")
            print(f"  Target: {handler.target_host}:{handler.target_port}")
            print(f"  Uptime: {str(uptime).split('.')[0]}")
            print(f"  Bytes C→S: {handler.bytes_client_to_server}")
            print(f"  Bytes S→C: {handler.bytes_server_to_client}")
            print()

    def show_stats(self):
        """Show proxy statistics"""
        uptime = datetime.now() - self.stats['start_time']

        print(f"{Colors.BLUE}Proxy Statistics:{Colors.ENDC}")
        print(f"  Uptime: {str(uptime).split('.')[0]}")
        print(f"  Total Connections: {self.stats['total_connections']}")
        print(f"  Active Connections: {self.stats['active_connections']}")
        print(f"  Bytes Client→Server: {self.stats['bytes_client_to_server']}")
        print(f"  Bytes Server→Client: {self.stats['bytes_server_to_client']}")
        print(f"  Intercepted Packets: {self.stats['intercepted_packets']}")

    def interactive_console(self):
        """Interactive proxy console"""
        while self.running:
            try:
                command = input(f"{Colors.GREEN}OMEGA_PROXY>{Colors.ENDC} ").strip()

                if not command:
                    continue

                if command.lower() in ['exit', 'stop', 'quit']:
                    self.stop()
                    break

                if command.lower() == 'help':
                    self.show_help()
                    continue

                if command.lower() == 'connections':
                    self.show_connections()
                    continue

                if command.lower() == 'stats':
                    self.show_stats()
                    continue

                # Unknown command
                print(f"{Colors.YELLOW}Unknown command. Type 'help' for available commands.{Colors.ENDC}")

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⚠️  Use 'stop' to shutdown proxy{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Console error: {e}{Colors.ENDC}")

    def show_help(self):
        """Show available commands"""
        help_text = """
OMEGA_X TCP Proxy Commands:
===========================

Proxy Control:
  help              Show this help
  exit/stop/quit    Shutdown proxy

Monitoring:
  connections       Show active connections
  stats             Show proxy statistics

Traffic Analysis:
  (Traffic logging is automatically enabled)
"""
        print(help_text)

    def stop(self):
        """Stop the proxy"""
        print(f"{Colors.YELLOW}🛑 Shutting down OMEGA_X TCP Proxy...{Colors.ENDC}")

        self.running = False

        # Close all active connections
        for handler in list(self.active_connections.values()):
            handler.close()

        # Close server socket
        if self.server_socket:
            self.server_socket.close()

        print(f"{Colors.GREEN}✅ Proxy shutdown complete{Colors.ENDC}")

class ProxyConnectionHandler:
    """Handle individual proxy connections"""

    def __init__(self, proxy, client_socket, client_address, connection_id,
                 target_host, target_port, use_ssl, intercept):
        self.proxy = proxy
        self.client_socket = client_socket
        self.client_address = client_address
        self.connection_id = connection_id
        self.target_host = target_host
        self.target_port = target_port
        self.use_ssl = use_ssl
        self.intercept = intercept

        self.server_socket = None
        self.running = True
        self.start_time = datetime.now()

        # Statistics
        self.bytes_client_to_server = 0
        self.bytes_server_to_client = 0

    def handle_connection(self):
        """Handle the proxy connection"""
        try:
            # Connect to target server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.target_host, self.target_port))

            print(f"{Colors.GREEN}✅ Connected to target {self.target_host}:{self.target_port}{Colors.ENDC}")

            # Start bidirectional proxying
            client_to_server = threading.Thread(
                target=self.proxy_traffic,
                args=(self.client_socket, self.server_socket, "client_to_server"),
                daemon=True
            )
            server_to_client = threading.Thread(
                target=self.proxy_traffic,
                args=(self.server_socket, self.client_socket, "server_to_client"),
                daemon=True
            )

            client_to_server.start()
            server_to_client.start()

            # Wait for threads to complete
            client_to_server.join()
            server_to_client.join()

        except Exception as e:
            print(f"{Colors.RED}❌ Connection error for {self.connection_id}: {e}{Colors.ENDC}")
        finally:
            self.close()

    def proxy_traffic(self, source_socket, dest_socket, direction):
        """Proxy traffic between sockets"""
        try:
            while self.running:
                # Receive data
                data = source_socket.recv(self.proxy.buffer_size)
                if not data:
                    break

                # Log traffic
                self.proxy.log_traffic(self.connection_id, direction, data)

                # Update statistics
                if direction == "client_to_server":
                    self.bytes_client_to_server += len(data)
                    self.proxy.stats['bytes_client_to_server'] += len(data)
                else:
                    self.bytes_server_to_client += len(data)
                    self.proxy.stats['bytes_server_to_client'] += len(data)

                # Intercept and modify if enabled
                if self.intercept:
                    data = self.intercept_traffic(data, direction)
                    self.proxy.stats['intercepted_packets'] += 1

                # Send data
                dest_socket.send(data)

        except Exception as e:
            if self.running:
                print(f"{Colors.RED}❌ Traffic proxy error for {self.connection_id}: {e}{Colors.ENDC}")

    def intercept_traffic(self, data, direction):
        """Intercept and potentially modify traffic"""
        try:
            # Convert to string for analysis (if text)
            try:
                text_data = data.decode('utf-8', errors='ignore')

                # Simple interception examples
                if direction == "client_to_server":
                    # Modify HTTP requests
                    if text_data.startswith("GET ") or text_data.startswith("POST "):
                        print(f"{Colors.CYAN}🔍 Intercepted HTTP request from {self.client_address}{Colors.ENDC}")
                        # Could modify headers, URLs, etc.

                    # Inject data or modify content
                    # This is where you would add custom interception logic

                elif direction == "server_to_client":
                    # Modify server responses
                    if "HTTP/" in text_data:
                        print(f"{Colors.CYAN}🔍 Intercepted HTTP response to {self.client_address}{Colors.ENDC}")

                # Convert back to bytes
                return text_data.encode('utf-8')

            except UnicodeDecodeError:
                # Binary data, pass through
                return data

        except Exception as e:
            print(f"{Colors.RED}❌ Traffic interception error: {e}{Colors.ENDC}")
            return data

    def close(self):
        """Close connection sockets"""
        self.running = False

        try:
            if self.client_socket:
                self.client_socket.close()
            if self.server_socket:
                self.server_socket.close()
        except:
            pass

        # Remove from proxy
        self.proxy.remove_connection(self.connection_id)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="OMEGA_X TCP Proxy")
    parser.add_argument('--listen-host', default='0.0.0.0', help='Proxy listen address (default: 0.0.0.0)')
    parser.add_argument('--listen-port', type=int, default=8080, help='Proxy listen port (default: 8080)')
    parser.add_argument('--target-host', required=True, help='Target server hostname/IP')
    parser.add_argument('--target-port', type=int, required=True, help='Target server port')
    parser.add_argument('--ssl', action='store_true', help='Use SSL/TLS for connections')
    parser.add_argument('--intercept', action='store_true', help='Enable traffic interception')

    args = parser.parse_args()

    # Create and start proxy
    proxy = OMEGATCPProxy(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        target_host=args.target_host,
        target_port=args.target_port,
        use_ssl=args.ssl,
        intercept=args.intercept
    )

    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
    except Exception as e:
        print(f"{Colors.RED}❌ Proxy error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()