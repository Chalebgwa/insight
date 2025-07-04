import sys
import socket
import random
import asyncio
from .print_status import print_status
from .colors import Colors


def subdomain_enumeration(domain, wordlist_path, max_tasks=50):
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

    print_status(f"Scanning {total} subdomains with {max_tasks} max tasks", "info")

    async def check_subdomain(subdomain, sem, loop):
        nonlocal processed
        full_domain = f"{subdomain}.{domain}"
        async with sem:
            try:
                infos = await loop.getaddrinfo(full_domain, None)
                ip = infos[0][4][0]
                found.append((full_domain, ip))
                result = (full_domain, ip)
            except socket.gaierror:
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
        loop = asyncio.get_running_loop()
        sem = asyncio.Semaphore(max_tasks)
        tasks = [asyncio.create_task(check_subdomain(sub, sem, loop)) for sub in subdomains]
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res:
                sub, ip = res
                print(f"\n  {Colors.GREEN}✓ Found: {sub} => {ip}{Colors.END}")
        print(f"\r{' ' * 70}")
        return found

    return asyncio.run(runner())
