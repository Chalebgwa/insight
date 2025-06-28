import sys
import socket
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from .print_status import print_status
from .colors import Colors


def subdomain_enumeration(domain, wordlist_path, threads=50):
    """Advanced subdomain enumeration with wildcard detection"""
    print_status(f"Enumerating subdomains for {domain}", "info")

    try:
        random_sub = f"{random.randint(100000,999999)}.{domain}"
        socket.gethostbyname(random_sub)
        print_status("Wildcard DNS detected! Results may contain false positives", "warning")
    except socket.gaierror:
        pass

    try:
        with open(wordlist_path) as f:
            subdomains = [line.strip() for line in f]
    except FileNotFoundError:
        print_status(f"Wordlist not found: {wordlist_path}", "error")
        return []

    found = []
    total = len(subdomains)
    processed = 0

    print_status(f"Scanning {total} subdomains with {threads} threads", "info")

    def check_subdomain(subdomain):
        nonlocal processed
        full_domain = f"{subdomain}.{domain}"
        try:
            ip = socket.gethostbyname(full_domain)
            found.append((full_domain, ip))
            return (full_domain, ip)
        except socket.gaierror:
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
        futures = [executor.submit(check_subdomain, sub) for sub in subdomains]
        for future in as_completed(futures):
            if future.result():
                sub, ip = future.result()
                print(f"\n  {Colors.GREEN}✓ Found: {sub} => {ip}{Colors.END}")

    print(f"\r{' ' * 70}")
    return found
