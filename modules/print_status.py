import logging

from .colors import Colors  # noqa: F401 (used for ColorFormatter in insight)

logger = logging.getLogger("insight")

def print_status(message, status="info", indent=0):
    """Log status messages while preserving colored console output."""
    level_map = {
        "info": logging.INFO,
        "success": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    logger.log(level_map.get(status, logging.INFO), message, extra={"indent": indent, "status": status})
