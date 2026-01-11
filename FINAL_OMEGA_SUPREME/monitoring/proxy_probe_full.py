import requests
import os
import time
import socket

def print_header(title):
    print("\n" + "="*20 + f" {title} " + "="*20)

# HTTP proxy test
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}
print_header("HTTP Proxy Test")
try:
    r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
    print("HTTP proxy response:", r.text)
except Exception as e:
    print("HTTP proxy test failed:", e)

# SOCKS5 proxy test
print_header("SOCKS5 Proxy Test")
try:
    proxies_socks = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080',
    }
    r = requests.get('http://httpbin.org/ip', proxies=proxies_socks, timeout=5)
    print("SOCKS5 proxy response:", r.text)
except Exception as e:
    print("SOCKS5 proxy test failed:", e)

# ICMP ping test
print_header("ICMP Ping Test")
response = os.system("ping -n 4 8.8.8.8")
if response == 0:
    print("Ping successful.")
else:
    print("Ping failed.")

time.sleep(1)

# Port scan (simple TCP connect)
print_header("Port Scan (TCP Connect)")
ports = [1080, 8080, 4433]
for port in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", port))
        print(f"Port {port}: OPEN")
    except Exception:
        print(f"Port {port}: CLOSED")
    finally:
        s.close()

time.sleep(1)

# HTTP probe
print_header("HTTP Probe on 8080")
try:
    r = requests.get('http://127.0.0.1:8080', timeout=3)
    print("HTTP probe response (8080):", r.status_code)
except Exception as e:
    print("HTTP probe failed (8080):", e)

# SSL probe
print_header("SSL Probe on 4433")
import ssl
try:
    context = ssl.create_default_context()
    with socket.create_connection(("127.0.0.1", 4433), timeout=3) as sock:
        with context.wrap_socket(sock, server_hostname="localhost") as ssock:
            print("SSL probe successful (4433):", ssock.version())
except Exception as e:
    print("SSL probe failed (4433):", e)
