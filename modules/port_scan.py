import sys
import socket
import asyncio
from urllib.parse import urlparse
from .print_status import print_status
from .colors import Colors


def port_scan(target, ports, max_tasks=100):
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

    print_status(f"Scanning {total} ports with {max_tasks} max tasks", "info")

    async def scan_port(port, sem):
        nonlocal processed
        async with sem:
            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.close()
                if hasattr(writer, 'wait_closed'):
                    await writer.wait_closed()
                service = services.get(port, "Unknown")
                open_ports.append((port, service))
                result = (port, service)
            except Exception:
                result = None
            processed += 1
            percent = int(processed / total * 100)
            bar_length = 40
            filled_length = int(bar_length * processed // total)
            bar = f"{Colors.BG_BLUE}{'█' * filled_length}{Colors.END}{'░' * (bar_length - filled_length)}"
            sys.stdout.write(f"\r  {bar} {percent}% ({processed}/{total}) ")
            sys.stdout.flush()
            return result

    async def runner():
        sem = asyncio.Semaphore(max_tasks)
        tasks = [asyncio.create_task(scan_port(p, sem)) for p in ports]
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res:
                port, service = res
                print(f"\n  {Colors.GREEN}✓ Port {port}/tcp open ({service}){Colors.END}")
        print(f"\r{' ' * 70}")
        return open_ports

    return asyncio.run(runner())
