import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import plugins.robots_checker as rc

class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


def test_robots_checker_parses_disallow(monkeypatch):
    data = "User-agent: *\nDisallow: /admin\nDisallow: /private\n"
    def mock_get(url, headers=None, timeout=5):
        return MockResponse(data, 200)
    monkeypatch.setattr(rc, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(rc, 'get_random_ua', lambda: 'UA')
    monkeypatch.setattr(rc.requests, 'get', mock_get)
    result = rc.run('https://example.com')
    assert result['found'] is True
    assert '/admin' in result['disallow']
    assert '/private' in result['disallow']
