from .colors import Colors

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
