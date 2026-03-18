import os
import sys
import asyncio
import pytest
from unittest.mock import MagicMock

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.port_scan import port_scan
from unittest.mock import AsyncMock

def test_port_scan_finds_open_ports(monkeypatch):
    # Mock status printing and progress bar
    import modules.port_scan as ps
    monkeypatch.setattr(ps, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'write', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'flush', lambda *a, **k: None)

    # Mock asyncio.open_connection on the module itself
    async def mock_open_connection(host, port):
        if port in [80, 443]:
            reader = MagicMock()
            writer = MagicMock()
            writer.wait_closed = AsyncMock()
            return reader, writer
        else:
            raise ConnectionRefusedError()

    monkeypatch.setattr(ps.asyncio, "open_connection", mock_open_connection)

    results = port_scan("http://example.com", [21, 80, 443, 8080])

    assert len(results) == 2
    ports = [r[0] for r in results]
    assert 80 in ports
    assert 443 in ports
    assert 21 not in ports

    # Check services
    service_map = dict(results)
    assert service_map[80] == "HTTP"
    assert service_map[443] == "HTTPS"

def test_port_scan_handles_unknown_services(monkeypatch):
    import modules.port_scan as ps
    monkeypatch.setattr(ps, 'print_status', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'write', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'flush', lambda *a, **k: None)

    async def mock_open_connection(host, port):
        reader = MagicMock()
        writer = MagicMock()
        writer.wait_closed = AsyncMock()
        return reader, writer

    monkeypatch.setattr(ps.asyncio, "open_connection", mock_open_connection)
    monkeypatch.setattr(sys.stdout, 'write', lambda *a, **k: None)
    monkeypatch.setattr(sys.stdout, 'flush', lambda *a, **k: None)

    results = port_scan("http://example.com", [12345])
    assert len(results) == 1
    assert results[0] == (12345, "Unknown")
