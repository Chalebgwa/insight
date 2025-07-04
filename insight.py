#!/usr/bin/env python3
"""Insight Web Pentesting Framework - Modular Edition"""
import argparse
import json
import sys
import time
import os
import logging
from urllib.parse import urlparse
from datetime import datetime

from modules.colors import BANNER, Colors
from modules.directory_bruteforce import directory_bruteforce
from modules.subdomain_enumeration import subdomain_enumeration
from modules.port_scan import port_scan
from modules.ssl_analyzer import ssl_analyzer
from modules.header_analyzer import header_analyzer
from modules.crawler import crawl_and_analyze
from modules.summary import print_summary


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Insight Web Pentesting Framework",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-d", "--dir-wordlist", help="Directory brute-force wordlist")
    parser.add_argument("-s", "--sub-wordlist", help="Subdomain enumeration wordlist")
    parser.add_argument(
        "-p",
        "--ports",
        nargs="+",
        type=int,
        default=[
            21,
            22,
            23,
            25,
            53,
            80,
            110,
            143,
            443,
            445,
            993,
            995,
            1433,
            3306,
            3389,
            5432,
            5900,
            6379,
            8000,
            8080,
            8443,
            9000,
            27017,
        ],
        help="Ports to scan",
    )
    parser.add_argument("-t", "--threads", type=int, default=30, help="Max threads")
    parser.add_argument(
        "-e",
        "--extensions",
        nargs="+",
        default=["", ".php", ".html", ".txt", ".bak", ".old", ".zip"],
        help="File extensions for brute-force",
    )
    parser.add_argument("-c", "--crawl-depth", type=int, default=2, help="Crawling depth")
    parser.add_argument("-o", "--output", help="Output file for results")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join(
        "logs", f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logger = logging.getLogger("insight")
    logger.setLevel(getattr(logging, args.log_level))

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, args.log_level))
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    class ColorFormatter(logging.Formatter):
        SYMBOLS = {
            "info": f"{Colors.BLUE}🛈{Colors.END}",
            "success": f"{Colors.GREEN}✓{Colors.END}",
            "warning": f"{Colors.YELLOW}⚠{Colors.END}",
            "error": f"{Colors.RED}✗{Colors.END}",
            "critical": f"{Colors.BG_RED}☠{Colors.END}",
        }

        def format(self, record):
            status = getattr(record, "status", record.levelname.lower())
            indent = getattr(record, "indent", 0)
            symbol = self.SYMBOLS.get(status, self.SYMBOLS["info"])
            message = super().format(record)
            return f"{' ' * indent}{symbol} {message}"

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, args.log_level))
    console_handler.setFormatter(ColorFormatter("%(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    if not args.url.startswith("http"):
        args.url = "http://" + args.url

    results = {
        "target": args.url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modules": {},
    }

    start_time = time.time()

    if args.dir_wordlist:
        dir_results = directory_bruteforce(
            args.url,
            args.dir_wordlist,
            extensions=args.extensions,
            threads=args.threads,
        )
        results["modules"]["directory_bruteforce"] = dir_results

    if args.sub_wordlist:
        domain = urlparse(args.url).netloc
        sub_results = subdomain_enumeration(domain, args.sub_wordlist, threads=args.threads)
        results["modules"]["subdomain_enumeration"] = sub_results

    port_results = port_scan(args.url, args.ports, threads=args.threads)
    results["modules"]["port_scan"] = port_results

    ssl_results = ssl_analyzer(args.url)
    results["modules"]["ssl_analyzer"] = ssl_results

    header_results = header_analyzer(args.url)
    results["modules"]["header_analyzer"] = header_results

    crawl_results = crawl_and_analyze(args.url, depth=args.crawl_depth)
    results["modules"]["crawler"] = crawl_results

    scan_duration = time.time() - start_time
    logger.info(
        f"Scan completed in {scan_duration:.2f} seconds",
        extra={"status": "success"},
    )

    print_summary(results)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(
            f"Results saved to {args.output}",
            extra={"status": "success"},
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.getLogger("insight").error("\nScan aborted by user")
        sys.exit(1)
