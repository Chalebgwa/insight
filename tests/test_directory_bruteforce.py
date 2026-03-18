import os
import sys
import pytest
import aiohttp

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.directory_bruteforce import directory_bruteforce

class MockAsyncResponse:
    def __init__(self, status, data=b""):
        self.status = status
        self.data = data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def read(self):
        return self.data

def test_directory_bruteforce_finds_paths(monkeypatch, tmp_path):
    # Create a temporary wordlist
    wordlist_file = tmp_path / "wordlist.txt"
    wordlist_file.write_text("admin\nconfig\nsecret")

    # Mock aiohttp.ClientSession.get
    def mock_get(self, url, **kwargs):
        if "admin" in url:
            return MockAsyncResponse(200, b"Found admin")
        if "config" in url:
            return MockAsyncResponse(200, b"Found config")
        return MockAsyncResponse(404)

    monkeypatch.setattr(aiohttp.ClientSession, "get", mock_get)

    # Mock status printing and progress bar to keep output clean
    import modules.directory_bruteforce as db
    monkeypatch.setattr(db, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'write', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'flush', lambda *a, **k: None)

    results = directory_bruteforce("http://target.com", str(wordlist_file), extensions=[""])

    # Verify results
    assert len(results) == 2
    found_urls = [r[0] for r in results]
    assert "http://target.com/admin" in found_urls
    assert "http://target.com/config" in found_urls
    assert "http://target.com/secret" not in found_urls

def test_directory_bruteforce_with_extensions(monkeypatch, tmp_path):
    wordlist_file = tmp_path / "wordlist.txt"
    wordlist_file.write_text("index")

    def mock_get(self, url, **kwargs):
        if "index.php" in url:
            return MockAsyncResponse(200, b"index.php")
        return MockAsyncResponse(404)

    monkeypatch.setattr(aiohttp.ClientSession, "get", mock_get)

    import modules.directory_bruteforce as db
    monkeypatch.setattr(db, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'write', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'flush', lambda *a, **k: None)

    results = directory_bruteforce("http://target.com", str(wordlist_file), extensions=[".php", ".html"])

    assert len(results) == 1
    assert results[0][0] == "http://target.com/index.php"
    assert results[0][1] == 200

def test_directory_bruteforce_file_not_found(monkeypatch):
    import modules.directory_bruteforce as db
    monkeypatch.setattr(db, 'print_status', lambda *a, **k: None)

    results = directory_bruteforce("http://target.com", "nonexistent.txt")
    assert results == []
