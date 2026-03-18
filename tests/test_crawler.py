import os
import sys
import pytest
import requests
from unittest.mock import MagicMock

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.crawler import crawl_and_analyze

class MockResponse:
    def __init__(self, text, url="http://example.com"):
        self.text = text
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

def test_crawler_finds_vulnerabilities(monkeypatch):
    # Mock responses for different URLs
    def mock_get(url, **kwargs):
        if url == "http://example.com":
            return MockResponse('<html><body><a href="/vulnerable">Link</a></body></html>', url)
        if url == "http://example.com/vulnerable":
            return MockResponse('<html><body>Potential SQL Injection: select * from users;</body></html>', url)
        return MockResponse('Not found', url)

    monkeypatch.setattr(requests, "get", mock_get)

    # Mock UI functions and sleep
    import modules.crawler as crawler
    monkeypatch.setattr(crawler, 'animated_progress_bar', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'print_table', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'sleep', lambda x: None)

    results = crawl_and_analyze("http://example.com", depth=1)

    assert len(results) == 1
    assert results[0][2] == "SQL Injection"
    assert "vulnerable" in results[0][1]

def test_crawler_finds_xss_in_url(monkeypatch):
    target = "http://example.com/?q=<script>alert(1)</script>"

    def mock_get(url, **kwargs):
        return MockResponse('<html><body>No vuln in body</body></html>', url)

    monkeypatch.setattr(requests, "get", mock_get)

    import modules.crawler as crawler
    monkeypatch.setattr(crawler, 'animated_progress_bar', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'print_table', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'sleep', lambda x: None)

    results = crawl_and_analyze(target, depth=0)

    assert any(r[2] == "XSS Vulnerability" for r in results)

def test_crawler_handles_request_exception(monkeypatch):
    def mock_get(url, **kwargs):
        raise requests.RequestException("Connection error")

    monkeypatch.setattr(requests, "get", mock_get)

    import modules.crawler as crawler
    monkeypatch.setattr(crawler, 'animated_progress_bar', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(crawler, 'sleep', lambda x: None)

    results = crawl_and_analyze("http://example.com", depth=0)
    assert results == []
