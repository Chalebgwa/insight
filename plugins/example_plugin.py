from modules.print_status import print_status

def run(target):
    """Simple example plugin"""
    print_status(f"Example plugin running for {target}", "info")
    return {"message": f"Example plugin executed for {target}"}
