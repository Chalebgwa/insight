import requests
from modules.print_status import print_status
from modules.random_ua import get_random_ua


def run(target):
    """Fetch and parse robots.txt for disallowed paths"""
    url = target.rstrip('/') + '/robots.txt'
    try:
        response = requests.get(url, headers={"User-Agent": get_random_ua()}, timeout=5)
        if response.status_code != 200:
            print_status(f"No robots.txt found at {url}", "warning")
            return {"found": False, "disallow": []}
        disallow = []
        for line in response.text.splitlines():
            line = line.strip()
            if line.lower().startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                if path:
                    disallow.append(path)
        print_status(f"Found robots.txt with {len(disallow)} disallowed entries", "success")
        return {"found": True, "disallow": disallow}
    except Exception as e:
        print_status(f"Failed to fetch robots.txt: {e}", "error")
        return {"found": False, "disallow": []}
