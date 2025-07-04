import sys
import asyncio
import aiohttp
from .print_status import print_status
from .progress import animated_progress_bar
from .colors import Colors
from .random_ua import get_random_ua


def directory_bruteforce(target, wordlist_path, extensions=None, max_tasks=20):
    """Advanced directory brute-forcing with extensions"""
    extensions = extensions or [""]
    print_status(f"Starting directory brute-force on {target}", "info")

    try:
        with open(wordlist_path) as f:
            base_words = [line.strip() for line in f]
    except FileNotFoundError:
        print_status(f"Wordlist not found: {wordlist_path}", "error")
        return []

    targets = []
    for word in base_words:
        for ext in extensions:
            targets.append(f"{word}{ext}")

    found = []
    headers = {"User-Agent": get_random_ua()}
    total = len(targets)
    processed = 0

    print_status(f"Scanning {total} paths with {max_tasks} max tasks", "info")

    async def check_path(path, sem, session):
        nonlocal processed
        url = f"{target.rstrip('/')}/{path}"
        async with sem:
            try:
                async with session.get(url, allow_redirects=False, timeout=5) as response:
                    if response.status < 400:
                        data = await response.read()
                        size = len(data)
                        found.append((url, response.status, size))
                        result = (url, response.status, size)
                    else:
                        result = None
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
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = [asyncio.create_task(check_path(p, sem, session)) for p in targets]
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if res:
                    url, status, size = res
                    print(f"\n  {Colors.GREEN}✓ Found: {url} [{status}] ({size} bytes){Colors.END}")
        print(f"\r{' ' * 70}")
        return found

    return asyncio.run(runner())
