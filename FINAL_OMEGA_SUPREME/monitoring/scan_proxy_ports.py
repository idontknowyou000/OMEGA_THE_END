import socket

ports = [1080, 8080, 4433]
results = {}
for port in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", port))
        results[port] = "OPEN"
    except Exception:
        results[port] = "CLOSED"
    finally:
        s.close()

for port, status in results.items():
    print(f"Port {port}: {status}")
