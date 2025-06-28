import re
import requests
from time import sleep
from urllib.parse import urljoin
from .progress import animated_progress_bar
from .print_status import print_status
from .print_table import print_table
from .random_ua import get_random_ua


def crawl_and_analyze(target, depth=2):
    """Advanced crawler with vulnerability pattern detection"""
    print_status(f"Crawling {target} (depth={depth})", "info")
    visited = set()
    to_visit = [(target, 0)]
    results = []

    vuln_patterns = {
        "SQL Injection": re.compile(r"select.*from|insert into|union all|' or '1'='1", re.I),
        "XSS Vulnerability": re.compile(r"<script>|alert\(|onerror=|javascript:", re.I),
        "Path Traversal": re.compile(r"\.\./|\.\.\\|etc/passwd", re.I),
        "Command Injection": re.compile(r";\s*\b(?:rm|ls|cat|echo|whoami|id|pwd)\b", re.I),
        "Sensitive Data Exposure": re.compile(r"password|secret|api[_-]?key|token", re.I),
    }

    total_pages = 0
    while to_visit:
        url, current_depth = to_visit.pop(0)
        if url in visited or current_depth > depth:
            continue
        visited.add(url)
        try:
            animated_progress_bar(f"Scanning page: {url}", 5)
            response = requests.get(url, headers={"User-Agent": get_random_ua()}, timeout=5)
            total_pages += 1
            for vuln_type, pattern in vuln_patterns.items():
                if pattern.search(response.text):
                    results.append(("CONTENT", url, vuln_type))
                    print_status(f"Potential {vuln_type} detected in: {url}", "warning")
            if "?" in url:
                for vuln_type, pattern in vuln_patterns.items():
                    if pattern.search(url):
                        results.append(("URL", url, vuln_type))
                        print_status(f"Potential {vuln_type} in URL: {url}", "warning")
            if current_depth < depth:
                for link in re.findall(r'href="(.*?)"', response.text):
                    absolute_link = urljoin(url, link)
                    if absolute_link.startswith(target) and absolute_link not in visited:
                        to_visit.append((absolute_link, current_depth + 1))
            sleep(0.1)
        except requests.RequestException:
            continue

    if results:
        print_table(
            ["Type", "URL", "Vulnerability"],
            results,
            "Vulnerability Scan Results",
        )
    else:
        print_status(f"No obvious vulnerabilities detected in {total_pages} crawled pages", "success")

    return results
