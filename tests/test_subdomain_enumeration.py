import os
import sys
import socket
import asyncio
import pytest

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.subdomain_enumeration import subdomain_enumeration

def test_subdomain_enumeration_finds_subdomains(monkeypatch, tmp_path):
    # Create a temporary wordlist
    wordlist_file = tmp_path / "subdomains.txt"
    wordlist_file.write_text("www\nmail\nnonexistent")

    # Mock socket.getaddrinfo since loop.getaddrinfo usually calls it
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if host == "www.example.com":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ("1.2.3.4", 0))]
        if host == "mail.example.com":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ("5.6.7.8", 0))]
        raise socket.gaierror(-2, "Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    # Mock socket.gethostbyname for wildcard check (simulate no wildcard)
    def mock_gethostbyname(host):
        raise socket.gaierror(-2, "Name or service not known")
    monkeypatch.setattr(socket, "gethostbyname", mock_gethostbyname)

    # Mock status printing and progress bar
    import modules.subdomain_enumeration as se
    monkeypatch.setattr(se, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'write', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'flush', lambda *a, **k: None)

    results = subdomain_enumeration("example.com", str(wordlist_file))

    assert len(results) == 2
    assert ("www.example.com", "1.2.3.4") in results
    assert ("mail.example.com", "5.6.7.8") in results

def test_subdomain_enumeration_detects_wildcard(monkeypatch, tmp_path):
    wordlist_file = tmp_path / "subdomains.txt"
    wordlist_file.write_text("www")

    # Mock wildcard detection
    def mock_gethostbyname(host):
        return "10.10.10.10"
    monkeypatch.setattr(socket, "gethostbyname", mock_gethostbyname)

    # Mock socket.getaddrinfo for actual enumeration
    def mock_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ("10.10.10.10", 0))]
    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    import modules.subdomain_enumeration as se
    mocked_statuses = []
    def mock_print_status(msg, status):
        mocked_statuses.append((msg, status))
    monkeypatch.setattr(se, 'print_status', mock_print_status)
    monkeypatch.setattr(sys.stdout, 'write', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'flush', lambda *a, **k: None)

    results = subdomain_enumeration("example.com", str(wordlist_file))

    assert any("Wildcard DNS detected" in s[0] for s in mocked_statuses)
    assert len(results) == 1
    assert results[0] == ("www.example.com", "10.10.10.10")

def test_subdomain_enumeration_file_not_found(monkeypatch):
    import modules.subdomain_enumeration as se
    monkeypatch.setattr(se, 'print_status', lambda *a, **k: None)

    results = subdomain_enumeration("example.com", "nonexistent.txt")
    assert results == []
