import sys
import time
from .print_status import print_status
from .colors import Colors

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
