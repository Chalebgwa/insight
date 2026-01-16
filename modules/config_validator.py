"""Configuration validator for Insight framework."""
from typing import Dict, Any, List
import os


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check for required fields if URL not provided via CLI
    if "url" in config and not isinstance(config["url"], str):
        errors.append("Config field 'url' must be a string")
    
    # Validate optional fields
    if "ports" in config:
        if not isinstance(config["ports"], list):
            errors.append("Config field 'ports' must be a list")
        else:
            for port in config["ports"]:
                if not isinstance(port, int) or port < 1 or port > 65535:
                    errors.append(f"Invalid port number: {port}")
    
    if "extensions" in config:
        if not isinstance(config["extensions"], list):
            errors.append("Config field 'extensions' must be a list")
        else:
            for ext in config["extensions"]:
                if not isinstance(ext, str):
                    errors.append(f"Extension must be a string: {ext}")
    
    if "max_tasks" in config:
        if not isinstance(config["max_tasks"], int) or config["max_tasks"] < 1:
            errors.append("Config field 'max_tasks' must be a positive integer")
    
    if "crawl_depth" in config:
        if not isinstance(config["crawl_depth"], int) or config["crawl_depth"] < 0:
            errors.append("Config field 'crawl_depth' must be a non-negative integer")
    
    # Validate file paths exist
    if "dir_wordlist" in config:
        if not isinstance(config["dir_wordlist"], str):
            errors.append("Config field 'dir_wordlist' must be a string")
        elif not os.path.exists(config["dir_wordlist"]):
            errors.append(f"Directory wordlist file not found: {config['dir_wordlist']}")
    
    if "sub_wordlist" in config:
        if not isinstance(config["sub_wordlist"], str):
            errors.append("Config field 'sub_wordlist' must be a string")
        elif not os.path.exists(config["sub_wordlist"]):
            errors.append(f"Subdomain wordlist file not found: {config['sub_wordlist']}")
    
    # Validate log level
    if "log_level" in config:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config["log_level"] not in valid_levels:
            errors.append(f"Invalid log_level: {config['log_level']}. Must be one of {valid_levels}")
    
    return errors
