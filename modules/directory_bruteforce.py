import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from .print_status import print_status
from .progress import animated_progress_bar
from .colors import Colors
from .random_ua import get_random_ua


def directory_bruteforce(target, wordlist_path, extensions=None, threads=20):
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

    print_status(f"Scanning {total} paths with {threads} threads", "info")

    def check_path(path):
        nonlocal processed
        url = f"{target}/{path}"
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
            if response.status_code < 400:
                size = len(response.content)
                found.append((url, response.status_code, size))
                return (url, response.status_code, size)
        except requests.RequestException:
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
        futures = [executor.submit(check_path, path) for path in targets]
        for future in as_completed(futures):
            if future.result():
                url, status, size = future.result()
                print(f"\n  {Colors.GREEN}✓ Found: {url} [{status}] ({size} bytes){Colors.END}")

    print(f"\r{' ' * 70}")
    return found
