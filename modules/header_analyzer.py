import requests
from .progress import animated_progress_bar
from .random_ua import get_random_ua
from .print_table import print_table
from .print_status import print_status
from .colors import Colors


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
        "X-XSS-Protection": {"score": 1, "found": False},
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

    print_table(
        ["Header", "Status", "Value"],
        results,
        "Security Header Analysis",
    )

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

    print_status(
        f"Security Header Score: {grade:.1f}% - {rating}{Colors.END}",
        "success" if grade >= 70 else "warning",
    )
    return results
