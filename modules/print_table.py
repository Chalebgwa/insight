from .colors import Colors

def print_table(headers, rows, title=None):
    """Print professional-looking tables with borders"""
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    table_width = sum(col_widths) + len(headers) * 3 + 1

    if title:
        title_pad = (table_width - len(title) - 4) // 2
        print(f"\n{Colors.BOLD}{Colors.BG_BLUE}{' ' * title_pad} {title} {' ' * title_pad}{Colors.END}")

    print(f"{Colors.GRAY}┌{'┬'.join(['─' * (w + 2) for w in col_widths])}┐{Colors.END}")

    header_cells = []
    for i, h in enumerate(headers):
        header_cells.append(f"{Colors.BOLD}{h.ljust(col_widths[i])}{Colors.END}")
    sep = f' {Colors.GRAY}│{Colors.END} '
    print(f"{Colors.GRAY}│{Colors.END} {sep.join(header_cells)} {Colors.GRAY}│{Colors.END}")

    print(f"{Colors.GRAY}├{'┼'.join(['─' * (w + 2) for w in col_widths])}┤{Colors.END}")

    for row in rows:
        row_cells = []
        for i, cell in enumerate(row):
            row_cells.append(str(cell).ljust(col_widths[i]))
        print(f"{Colors.GRAY}│{Colors.END} {' │ '.join(row_cells)} {Colors.GRAY}│{Colors.END}")

    print(f"{Colors.GRAY}└{'┴'.join(['─' * (w + 2) for w in col_widths])}┘{Colors.END}")
