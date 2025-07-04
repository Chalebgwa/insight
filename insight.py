#!/usr/bin/env python3
"""Insight Web Pentesting Framework - Modular Edition"""
import argparse
import json
import sys
import time
from urllib.parse import urlparse
from datetime import datetime
import yaml

from modules.colors import BANNER
from modules.directory_bruteforce import directory_bruteforce
from modules.subdomain_enumeration import subdomain_enumeration
from modules.port_scan import port_scan
from modules.ssl_analyzer import ssl_analyzer
from modules.header_analyzer import header_analyzer
from modules.crawler import crawl_and_analyze
from modules.summary import print_summary
from modules.print_status import print_status


def main():
    print(BANNER)

    # Parse optional configuration file first
    config_parser = argparse.ArgumentParser(add_help=False)
    config_parser.add_argument("--config", help="YAML configuration file")
    config_args, remaining = config_parser.parse_known_args()

    config = {}
    if config_args.config:
        try:
            with open(config_args.config) as f:
                config = yaml.safe_load(f) or {}
            print_status(f"Loaded configuration from {config_args.config}", "info")
        except FileNotFoundError:
            print_status(f"Config file not found: {config_args.config}", "error")
            sys.exit(1)
        except yaml.YAMLError as e:
            print_status(f"Invalid config file: {e}", "error")
            sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Insight Web Pentesting Framework",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[config_parser],
    )
    parser.add_argument(
        "-u",
        "--url",
        required=not config.get("url"),
        default=config.get("url"),
        help="Target URL",
    )
    parser.add_argument(
        "-d",
        "--dir-wordlist",
        default=config.get("dir_wordlist"),
        help="Directory brute-force wordlist",
    )
    parser.add_argument(
        "-s",
        "--sub-wordlist",
        default=config.get("sub_wordlist"),
        help="Subdomain enumeration wordlist",
    )
    parser.add_argument(
        "-p",
        "--ports",
        nargs="+",
        type=int,
        default=config.get(
            "ports",
            [
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
        ),
        help="Ports to scan",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=config.get("threads", 30),
        help="Max threads",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        nargs="+",
        default=config.get("extensions", ["", ".php", ".html", ".txt", ".bak", ".old", ".zip"]),
        help="File extensions for brute-force",
    )
    parser.add_argument(
        "-c",
        "--crawl-depth",
        type=int,
        default=config.get("crawl_depth", 2),
        help="Crawling depth",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=config.get("output"),
        help="Output file for results",
    )

    args = parser.parse_args(remaining)

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
    print_status(f"Scan completed in {scan_duration:.2f} seconds", "success")

    print_summary(results)

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
