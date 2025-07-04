import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest

from modules import header_analyzer as ha

class MockResponse:
    def __init__(self, headers):
        self.headers = headers


def test_header_analyzer_detects_headers(monkeypatch):
    sample_headers = {
        'Content-Security-Policy': 'default-src self',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY'
    }

    def mock_get(url, headers=None, timeout=5):
        return MockResponse(sample_headers)

    monkeypatch.setattr(ha, 'animated_progress_bar', lambda *a, **k: None)
    monkeypatch.setattr(ha, 'print_table', lambda *a, **k: None)
    monkeypatch.setattr(ha, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(ha, 'get_random_ua', lambda: 'UA')
    monkeypatch.setattr(ha.requests, 'get', mock_get)

    results = ha.header_analyzer('http://example.com')
    result_map = {h: (status, value) for h, status, value in results}

    assert 'Content-Security-Policy' in result_map
    assert 'PRESENT' in result_map['Content-Security-Policy'][0]
    assert result_map['Content-Security-Policy'][1] == 'default-src self'

    assert 'Strict-Transport-Security' in result_map
    assert 'MISSING' in result_map['Strict-Transport-Security'][0]
