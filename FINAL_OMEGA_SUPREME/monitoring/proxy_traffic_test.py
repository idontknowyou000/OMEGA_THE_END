import requests
import os
import time

# HTTP proxy test
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}

print("Testing HTTP proxy with requests...")
try:
    r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
    print("HTTP proxy response:", r.text)
except Exception as e:
    print("HTTP proxy test failed:", e)

# SOCKS5 proxy test (requires requests[socks])
try:
    import socks
    proxies_socks = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080',
    }
    r = requests.get('http://httpbin.org/ip', proxies=proxies_socks, timeout=5)
    print("SOCKS5 proxy response:", r.text)
except Exception as e:
    print("SOCKS5 proxy test failed:", e)

# ICMP ping test
print("Pinging 8.8.8.8...")
response = os.system("ping -n 4 8.8.8.8")
if response == 0:
    print("Ping successful.")
else:
    print("Ping failed.")

time.sleep(2)
