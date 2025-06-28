from .print_status import print_status
from .colors import Colors


def print_summary(results):
    """Print a professional summary of findings"""
    critical_count = 0
    warning_count = 0
    info_count = 0

    for module, data in results["modules"].items():
        if module == "ssl_analyzer":
            if any("vulnerable" in str(item).lower() for item in data):
                critical_count += 1
        elif module == "header_analyzer":
            if any("MISSING" in str(item) for item in data):
                warning_count += 1
        elif module == "crawler" and data:
            critical_count += len(data)

    summary_rows = [
        ("Target", results["target"]),
        ("Scan Date", results["timestamp"]),
        ("Critical Findings", f"{Colors.RED}{critical_count}{Colors.END}"),
        ("Warnings", f"{Colors.YELLOW}{warning_count}{Colors.END}"),
        ("Informational", f"{Colors.BLUE}{info_count}{Colors.END}"),
    ]

    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Scan Summary:{Colors.END}")
    for row in summary_rows:
        print(f"  {Colors.BOLD}{row[0]}:{Colors.END} {row[1]}")

    if critical_count > 0:
        status = f"{Colors.BG_RED} CRITICAL {Colors.END}"
    elif warning_count > 0:
        status = f"{Colors.BG_YELLOW} WARNING {Colors.END}"
    else:
        status = f"{Colors.BG_GREEN} SECURE {Colors.END}"

    print(f"\n  Overall Status: {status}")
