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
import yaml

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich import box

from modules.colors import BANNER, Colors, get_banner, console
from modules.directory_bruteforce import directory_bruteforce
from modules.subdomain_enumeration import subdomain_enumeration
from modules.port_scan import port_scan
from modules.ssl_analyzer import ssl_analyzer
from modules.header_analyzer import header_analyzer
from modules.crawler import crawl_and_analyze
from modules.summary import print_summary
from modules.config_validator import validate_config

from modules.print_status import print_status
from modules.plugin_loader import load_plugins
from modules import generate_html_report, generate_pdf_report



def main():
    # Display enhanced banner with Rich
    try:
        console.print(get_banner())
    except Exception:
        # Fallback to classic banner if Rich fails
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
            
            # Validate configuration
            validation_errors = validate_config(config)
            if validation_errors:
                print_status("Configuration validation failed:", "error")
                for error in validation_errors:
                    print_status(f"  - {error}", "error")
                sys.exit(1)
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

        "-m",
        "--max-tasks",
        type=int,
        default=30,
        help="Maximum concurrent tasks",

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
    parser.add_argument(
        "--log-level",
        default=config.get("log_level", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    parser.add_argument(
        "--html-report",
        default=config.get("html_report"),
        help="Write HTML report to file",
    )
    parser.add_argument(
        "--pdf-report",
        default=config.get("pdf_report"),
        help="Write PDF report to file",
    )


    args = parser.parse_args(remaining)


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

    # Enhanced URL validation
    if not args.url.startswith("http"):
        args.url = "http://" + args.url
    
    # Validate URL format
    try:
        parsed = urlparse(args.url)
        if not parsed.netloc:
            print_status("Invalid URL format. Please provide a valid URL.", "error")
            sys.exit(1)
    except Exception as e:
        print_status(f"URL parsing error: {e}", "error")
        sys.exit(1)

    # Validate wordlist files exist if provided
    if args.dir_wordlist and not os.path.exists(args.dir_wordlist):
        print_status(f"Directory wordlist file not found: {args.dir_wordlist}", "error")
        sys.exit(1)
    
    if args.sub_wordlist and not os.path.exists(args.sub_wordlist):
        print_status(f"Subdomain wordlist file not found: {args.sub_wordlist}", "error")
        sys.exit(1)

    results = {
        "target": args.url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modules": {},
        "performance": {},
    }

    start_time = time.time()

    # Track performance metrics for each module
    module_times = {}

    if args.dir_wordlist:
        module_start = time.time()
        dir_results = directory_bruteforce(
            args.url,
            args.dir_wordlist,
            extensions=args.extensions,
            max_tasks=args.max_tasks,
        )
        module_times["directory_bruteforce"] = time.time() - module_start
        results["modules"]["directory_bruteforce"] = dir_results

    if args.sub_wordlist:
        module_start = time.time()
        domain = urlparse(args.url).netloc
        sub_results = subdomain_enumeration(domain, args.sub_wordlist, max_tasks=args.max_tasks)
        module_times["subdomain_enumeration"] = time.time() - module_start
        results["modules"]["subdomain_enumeration"] = sub_results

    module_start = time.time()
    port_results = port_scan(args.url, args.ports, max_tasks=args.max_tasks)
    module_times["port_scan"] = time.time() - module_start
    results["modules"]["port_scan"] = port_results

    module_start = time.time()
    ssl_results = ssl_analyzer(args.url)
    module_times["ssl_analyzer"] = time.time() - module_start
    results["modules"]["ssl_analyzer"] = ssl_results

    module_start = time.time()
    header_results = header_analyzer(args.url)
    module_times["header_analyzer"] = time.time() - module_start
    results["modules"]["header_analyzer"] = header_results

    module_start = time.time()
    crawl_results = crawl_and_analyze(args.url, depth=args.crawl_depth)
    module_times["crawler"] = time.time() - module_start
    results["modules"]["crawler"] = crawl_results

    plugins = load_plugins()
    for plugin in plugins:
        name = plugin.__name__.split('.')[-1]
        try:
            module_start = time.time()
            plugin_results = plugin.run(args.url)
            module_times[f"plugin_{name}"] = time.time() - module_start
            results["modules"][name] = plugin_results
        except Exception as e:
            print_status(f"Plugin {name} failed: {e}", "error")

    scan_duration = time.time() - start_time
    results["performance"]["total_duration"] = round(scan_duration, 2)
    results["performance"]["module_times"] = {k: round(v, 2) for k, v in module_times.items()}
    
    # Display performance metrics with Rich
    try:
        perf_table = Table(title="⚡ Performance Metrics", box=box.ROUNDED)
        perf_table.add_column("Module", style="cyan", no_wrap=True)
        perf_table.add_column("Duration", style="magenta", justify="right")
        
        for module, duration in module_times.items():
            perf_table.add_row(module.replace("_", " ").title(), f"{duration:.2f}s")
        
        perf_table.add_row("─" * 30, "─" * 10, style="dim")
        perf_table.add_row("[bold]Total Scan Time[/bold]", f"[bold green]{scan_duration:.2f}s[/bold green]")
        
        console.print("\n")
        console.print(perf_table)
        console.print("\n")
    except Exception:
        pass
    
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

    if args.html_report:
        generate_html_report(results, args.html_report)
        print_status(f"HTML report saved to {args.html_report}", "success")

    if args.pdf_report:
        generate_pdf_report(results, args.pdf_report)
        print_status(f"PDF report saved to {args.pdf_report}", "success")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.getLogger("insight").error("\nScan aborted by user")
        sys.exit(1)
