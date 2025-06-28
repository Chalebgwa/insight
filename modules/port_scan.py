import sys
import socket
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from .print_status import print_status
from .colors import Colors


def port_scan(target, ports, threads=100):
    """Advanced port scanning with service detection"""
    print_status(f"Scanning ports for {target}", "info")
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]

    services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        993: "IMAPS",
        995: "POP3S",
        1433: "MSSQL",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        6379: "Redis",
        8000: "HTTP Alt",
        8080: "HTTP Proxy",
        8443: "HTTPS Alt",
        9000: "PHP-FPM",
        27017: "MongoDB",
    }

    open_ports = []
    total = len(ports)
    processed = 0

    print_status(f"Scanning {total} ports with {threads} threads", "info")

    def scan_port(port):
        nonlocal processed
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    service = services.get(port, "Unknown")
                    open_ports.append((port, service))
                    return (port, service)
        except Exception:
            return None
        finally:
            processed += 1
            percent = int(processed / total * 100)
            bar_length = 40
            filled_length = int(bar_length * processed // total)
            bar = f"{Colors.BG_BLUE}{'█' * filled_length}{Colors.END}{'░' * (bar_length - filled_length)}"
            sys.stdout.write(f"\r  {bar} {percent}% ({processed}/{total}) ")
            sys.stdout.flush()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(scan_port, port) for port in ports]
        for future in as_completed(futures):
            if future.result():
                port, service = future.result()
                print(f"\n  {Colors.GREEN}✓ Port {port}/tcp open ({service}){Colors.END}")

    print(f"\r{' ' * 70}")
    return open_ports
