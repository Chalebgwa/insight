import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse
from .progress import animated_progress_bar
from .print_table import print_table
from .print_status import print_status
from .colors import Colors


def ssl_analyzer(target):
    """Comprehensive SSL/TLS analyzer"""
    animated_progress_bar("Analyzing SSL/TLS configuration", 20)

    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    port = 443

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                tls_version = ssock.version()

                exp_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (exp_date - datetime.now()).days

                issuer = dict(x[0] for x in cert['issuer'])['organizationName']
                subject = dict(x[0] for x in cert['subject'])['commonName']

                vulns = []
                if "TLSv1" in tls_version:
                    vulns.append("TLSv1 (POODLE vulnerable)")
                if "RC4" in cipher[0]:
                    vulns.append("RC4 cipher (weak)")
                if days_left < 30:
                    vulns.append(f"Expiring in {days_left} days")

                results = [
                    ("Host", host),
                    ("Issuer", issuer),
                    ("Subject", subject),
                    ("Expiration", f"{exp_date} ({days_left} days)"),
                    ("TLS Version", tls_version),
                    ("Cipher", f"{cipher[0]} {cipher[1]} bits"),
                    ("Vulnerabilities", ", ".join(vulns) if vulns else "None found")
                ]

                print_table(
                    ["Setting", "Value"],
                    [(f"{Colors.BOLD}{k}{Colors.END}", v) for k, v in results],
                    "SSL/TLS Analysis",
                )
                return results
    except Exception as e:
        print_status(f"SSL analysis failed: {str(e)}", "error")
        return []
