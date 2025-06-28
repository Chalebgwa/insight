#!/usr/bin/env python3
"""
Insight Web Pentesting Framework - Professional Terminal Toolkit
"""

import argparse
import requests
import socket
import ssl
import os
import sys
import json
import random
import re
import time
from time import sleep
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ANSI Escape Codes for professional UI
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_YELLOW = '\033[43m'

# Professional Banner
BANNER = f"""
{Colors.BLUE}{Colors.BOLD}

!  ░▒▓█▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░      
!  ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
!  ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
!  ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░▒▓████████▓▒░  ░▒▓█▓▒░          
!  ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
!  ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
!  ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░          
!                                                                                      
                                                                              
              
{Colors.END}{Colors.CYAN}{Colors.BOLD}
            Advanced Web Pentesting Suite
        {Colors.GREEN}Version 2.1 • {datetime.now().strftime('%Y')}{Colors.END}
"""

def print_status(message, status="info", indent=0):
    """Professional status printer with indicators"""
    symbols = {
        "info": f"{Colors.BLUE}🛈{Colors.END}",
        "success": f"{Colors.GREEN}✓{Colors.END}",
        "warning": f"{Colors.YELLOW}⚠{Colors.END}",
        "error": f"{Colors.RED}✗{Colors.END}",
        "critical": f"{Colors.BG_RED}☠{Colors.END}"
    }
    indent_str = " " * indent
    print(f"{indent_str}{symbols[status]} {message}")

def print_table(headers, rows, title=None):
    """Print professional-looking tables with borders"""
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Table width
    table_width = sum(col_widths) + len(headers) * 3 + 1
    
    # Print title
    if title:
        title_pad = (table_width - len(title) - 4) // 2
        print(f"\n{Colors.BOLD}{Colors.BG_BLUE}{' ' * title_pad} {title} {' ' * title_pad}{Colors.END}")
    
    # Top border
    print(f"{Colors.GRAY}┌{'┬'.join(['─' * (w + 2) for w in col_widths])}┐{Colors.END}")
    
    # Header row
    header_cells = []
    for i, h in enumerate(headers):
        header_cells.append(f"{Colors.BOLD}{h.ljust(col_widths[i])}{Colors.END}")
    sep = f' {Colors.GRAY}│{Colors.END} '
    print(f"{Colors.GRAY}│{Colors.END} {sep.join(header_cells)} {Colors.GRAY}│{Colors.END}")
    
    # Separator
    print(f"{Colors.GRAY}├{'┼'.join(['─' * (w + 2) for w in col_widths])}┤{Colors.END}")
    
    # Data rows
    for row in rows:
        row_cells = []
        for i, cell in enumerate(row):
            row_cells.append(str(cell).ljust(col_widths[i]))
        print(f"{Colors.GRAY}│{Colors.END} {' │ '.join(row_cells)} {Colors.GRAY}│{Colors.END}")
    
    # Bottom border
    print(f"{Colors.GRAY}└{'┴'.join(['─' * (w + 2) for w in col_widths])}┘{Colors.END}")

def animated_progress_bar(description, duration, success=True):
    """Display an animated progress bar"""
    print_status(f"{description}...", "info")
    for i in range(duration):
        percent = int((i + 1) / duration * 100)
        bar_length = 30
        filled_length = int(bar_length * (i + 1) // duration)
        bar = f"{Colors.BG_GREEN if success else Colors.BG_RED}{'█' * filled_length}{Colors.END}{'░' * (bar_length - filled_length)}"
        sys.stdout.write(f"\r  {bar} {percent}% ")
        sys.stdout.flush()
        time.sleep(0.05)
    print(f"\r  {Colors.GREEN if success else Colors.RED}✔ Complete{' ' * 50}{Colors.END}")

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

    # Generate targets with extensions
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
    
    print(f"\r{' ' * 70}")  # Clear progress line
    return found

def subdomain_enumeration(domain, wordlist_path, threads=50):
    """Advanced subdomain enumeration with wildcard detection"""
    print_status(f"Enumerating subdomains for {domain}", "info")
    
    # Check for wildcard DNS
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
    
    print(f"\r{' ' * 70}")  # Clear progress line
    return found

def port_scan(target, ports, threads=100):
    """Advanced port scanning with service detection"""
    print_status(f"Scanning ports for {target}", "info")
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    
    # Common service detection
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
        27017: "MongoDB"
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
    
    print(f"\r{' ' * 70}")  # Clear progress line
    return open_ports

def ssl_analyzer(target):
    """Comprehensive SSL/TLS analyzer"""
    animated_progress_bar("Analyzing SSL/TLS configuration", 20)
    
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    port = 443
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                tls_version = ssock.version()
                
                # Certificate expiration
                exp_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (exp_date - datetime.now()).days
                
                # Certificate validation
                issuer = dict(x[0] for x in cert['issuer'])['organizationName']
                subject = dict(x[0] for x in cert['subject'])['commonName']
                
                # Vulnerabilities
                vulns = []
                if "TLSv1" in tls_version:
                    vulns.append("TLSv1 (POODLE vulnerable)")
                if "RC4" in cipher[0]:
                    vulns.append("RC4 cipher (weak)")
                if days_left < 30:
                    vulns.append(f"Expiring in {days_left} days")
                
                results = [
                    ("Host", host),
                    ("Issuer", issuer),
                    ("Subject", subject),
                    ("Expiration", f"{exp_date} ({days_left} days)"),
                    ("TLS Version", tls_version),
                    ("Cipher", f"{cipher[0]} {cipher[1]} bits"),
                    ("Vulnerabilities", ", ".join(vulns) if vulns else "None found")
                ]
                
                # Print results in a table
                print_table(
                    ["Setting", "Value"], 
                    [(f"{Colors.BOLD}{k}{Colors.END}", v) for k, v in results],
                    "SSL/TLS Analysis"
                )
                
                return results
    except Exception as e:
        print_status(f"SSL analysis failed: {str(e)}", "error")
        return []

def get_random_ua():
    """Return random User-Agent for stealth"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
    ]
    return random.choice(user_agents)

def header_analyzer(target):
    """Security header analyzer with scoring"""
    animated_progress_bar("Analyzing HTTP security headers", 15)
    
    headers = requests.get(target, headers={"User-Agent": get_random_ua()}, timeout=5).headers
    
    security_headers = {
        "Content-Security-Policy": {"score": 3, "found": False},
        "X-Content-Type-Options": {"score": 2, "found": False},
        "Strict-Transport-Security": {"score": 3, "found": False},
        "X-Frame-Options": {"score": 2, "found": False},
        "Referrer-Policy": {"score": 1, "found": False},
        "Feature-Policy": {"score": 1, "found": False},
        "Permissions-Policy": {"score": 1, "found": False},
        "X-XSS-Protection": {"score": 1, "found": False}
    }
    
    results = []
    total_score = 0
    max_score = sum(item["score"] for item in security_headers.values())
    
    for header, data in security_headers.items():
        if header in headers:
            security_headers[header]["found"] = True
            total_score += data["score"]
            results.append((header, f"{Colors.GREEN}PRESENT{Colors.END}", headers[header]))
        else:
            results.append((header, f"{Colors.RED}MISSING{Colors.END}", ""))

    # Print table
    print_table(
        ["Header", "Status", "Value"], 
        results,
        "Security Header Analysis"
    )
    
    # Calculate security grade
    grade = (total_score / max_score) * 100
    if grade >= 90:
        rating = f"{Colors.GREEN}A+ (Excellent)"
    elif grade >= 80:
        rating = f"{Colors.GREEN}A (Good)"
    elif grade >= 70:
        rating = f"{Colors.YELLOW}B (Fair)"
    elif grade >= 60:
        rating = f"{Colors.YELLOW}C (Poor)"
    else:
        rating = f"{Colors.RED}F (Critical)"
    
    print_status(f"Security Header Score: {grade:.1f}% - {rating}{Colors.END}", 
                "success" if grade >= 70 else "warning")
    
    return results

def crawl_and_analyze(target, depth=2):
    """Advanced crawler with vulnerability pattern detection"""
    print_status(f"Crawling {target} (depth={depth})", "info")
    visited = set()
    to_visit = [(target, 0)]
    results = []
    
    # Vulnerability patterns
    vuln_patterns = {
        "SQL Injection": re.compile(r"select.*from|insert into|union all|' or '1'='1", re.I),
        "XSS Vulnerability": re.compile(r"<script>|alert\(|onerror=|javascript:", re.I),
        "Path Traversal": re.compile(r"\.\./|\.\.\\\\|etc/passwd", re.I),
        "Command Injection": re.compile(r";\s*\b(?:rm|ls|cat|echo|whoami|id|pwd)\b", re.I),
        "Sensitive Data Exposure": re.compile(r"password|secret|api[_-]?key|token", re.I)
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
            
            # Check for vulnerabilities in content
            for vuln_type, pattern in vuln_patterns.items():
                if pattern.search(response.text):
                    results.append(("CONTENT", url, vuln_type))
                    print_status(f"Potential {vuln_type} detected in: {url}", "warning")
            
            # Check for vulnerabilities in URL parameters
            if "?" in url:
                for vuln_type, pattern in vuln_patterns.items():
                    if pattern.search(url):
                        results.append(("URL", url, vuln_type))
                        print_status(f"Potential {vuln_type} in URL: {url}", "warning")
            
            # Extract links
            if current_depth < depth:
                for link in re.findall(r'href="(.*?)"', response.text):
                    absolute_link = urljoin(url, link)
                    if absolute_link.startswith(target) and absolute_link not in visited:
                        to_visit.append((absolute_link, current_depth + 1))
            
            sleep(0.1)  # Polite crawling
            
        except requests.RequestException:
            continue
    
    if results:
        print_table(
            ["Type", "URL", "Vulnerability"], 
            results,
            "Vulnerability Scan Results"
        )
    else:
        print_status(f"No obvious vulnerabilities detected in {total_pages} crawled pages", "success")
    
    return results

def print_summary(results):
    """Print a professional summary of findings"""
    critical_count = 0
    warning_count = 0
    info_count = 0
    
    # Count findings by severity
    for module, data in results["modules"].items():
        if module == "ssl_analyzer":
            if any("vulnerable" in str(item).lower() for item in data):
                critical_count += 1
        elif module == "header_analyzer":
            if any("MISSING" in str(item) for item in data):
                warning_count += 1
        elif module == "crawler" and data:
            critical_count += len(data)
    
    # Create summary table
    summary_rows = [
        ("Target", results["target"]),
        ("Scan Date", results["timestamp"]),
        ("Critical Findings", f"{Colors.RED}{critical_count}{Colors.END}"),
        ("Warnings", f"{Colors.YELLOW}{warning_count}{Colors.END}"),
        ("Informational", f"{Colors.BLUE}{info_count}{Colors.END}")
    ]
    
    # Print summary
    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Scan Summary:{Colors.END}")
    for row in summary_rows:
        print(f"  {Colors.BOLD}{row[0]}:{Colors.END} {row[1]}")
    
    # Print overall status
    if critical_count > 0:
        status = f"{Colors.BG_RED} CRITICAL {Colors.END}"
    elif warning_count > 0:
        status = f"{Colors.BG_YELLOW} WARNING {Colors.END}"
    else:
        status = f"{Colors.BG_GREEN} SECURE {Colors.END}"
    
    print(f"\n  Overall Status: {status}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Insight Web Pentesting Framework",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-d", "--dir-wordlist", help="Directory brute-force wordlist")
    parser.add_argument("-s", "--sub-wordlist", help="Subdomain enumeration wordlist")
    parser.add_argument("-p", "--ports", nargs="+", type=int, 
                        default=[21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
                                 993, 995, 1433, 3306, 3389, 5432, 5900, 6379, 
                                 8000, 8080, 8443, 9000, 27017], 
                        help="Ports to scan")
    parser.add_argument("-t", "--threads", type=int, default=30, help="Max threads")
    parser.add_argument("-e", "--extensions", nargs="+", 
                        default=["", ".php", ".html", ".txt", ".bak", ".old", ".zip"], 
                        help="File extensions for brute-force")
    parser.add_argument("-c", "--crawl-depth", type=int, default=2, help="Crawling depth")
    parser.add_argument("-o", "--output", help="Output file for results")
    
    args = parser.parse_args()
    
    if not args.url.startswith("http"):
        args.url = "http://" + args.url
    
    results = {
        "target": args.url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modules": {}
    }
    
    start_time = time.time()
    
    # Run modules
    if args.dir_wordlist:
        dir_results = directory_bruteforce(
            args.url, 
            args.dir_wordlist,
            extensions=args.extensions,
            threads=args.threads
        )
        results["modules"]["directory_bruteforce"] = dir_results
    
    if args.sub_wordlist:
        domain = urlparse(args.url).netloc
        sub_results = subdomain_enumeration(
            domain, 
            args.sub_wordlist,
            threads=args.threads
        )
        results["modules"]["subdomain_enumeration"] = sub_results
    
    port_results = port_scan(args.url, args.ports, threads=args.threads)
    results["modules"]["port_scan"] = port_results
    
    ssl_results = ssl_analyzer(args.url)
    results["modules"]["ssl_analyzer"] = ssl_results
    
    header_results = header_analyzer(args.url)
    results["modules"]["header_analyzer"] = header_results
    
    crawl_results = crawl_and_analyze(args.url, depth=args.crawl_depth)
    results["modules"]["crawler"] = crawl_results
    
    # Calculate scan duration
    scan_duration = time.time() - start_time
    print_status(f"Scan completed in {scan_duration:.2f} seconds", "success")
    
    # Print summary
    print_summary(results)
    
    # Save results if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print_status(f"Results saved to {args.output}", "success")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_status("\nScan aborted by user", "error")
        sys.exit(1) 