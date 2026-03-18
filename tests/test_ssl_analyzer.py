import os
import sys
import socket
import ssl
import pytest
from unittest.mock import MagicMock, patch

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.ssl_analyzer import ssl_analyzer

def test_ssl_analyzer_success(monkeypatch):
    # Mock certificate data
    mock_cert = {
        'notAfter': 'Jan 01 00:00:00 2030 GMT',
        'issuer': ((('organizationName', 'Mock CA'),),),
        'subject': ((('commonName', 'example.com'),),)
    }

    # Mock SSL context and socket
    mock_ssock = MagicMock()
    mock_ssock.getpeercert.return_value = mock_cert
    mock_ssock.cipher.return_value = ('ECDHE-RSA-AES128-GCM-SHA256', 'TLSv1.3', 128)
    mock_ssock.version.return_value = 'TLSv1.3'

    # Context manager mock for ssock
    mock_ssock.__enter__.return_value = mock_ssock

    mock_context = MagicMock()
    mock_context.wrap_socket.return_value = mock_ssock

    monkeypatch.setattr(ssl, "create_default_context", lambda: mock_context)

    # Mock socket.create_connection
    mock_sock = MagicMock()
    mock_sock.__enter__.return_value = mock_sock
    monkeypatch.setattr(socket, "create_connection", lambda address: mock_sock)

    # Mock UI functions
    import modules.ssl_analyzer as sa
    monkeypatch.setattr(sa, 'animated_progress_bar', lambda *a, **k: None)
    monkeypatch.setattr(sa, 'print_table', lambda *a, **k: None)
    monkeypatch.setattr(sa, 'print_status', lambda *a, **k: None)

    results = ssl_analyzer("https://example.com")

    assert len(results) > 0
    result_dict = dict(results)
    assert result_dict["Host"] == "example.com"
    assert result_dict["Issuer"] == "Mock CA"
    assert result_dict["Subject"] == "example.com"
    assert result_dict["TLS Version"] == "TLSv1.3"
    assert "None found" in result_dict["Vulnerabilities"]

def test_ssl_analyzer_vulnerabilities(monkeypatch):
    mock_cert = {
        'notAfter': 'Jan 01 00:00:00 2020 GMT', # Expired
        'issuer': ((('organizationName', 'Mock CA'),),),
        'subject': ((('commonName', 'example.com'),),)
    }

    mock_ssock = MagicMock()
    mock_ssock.getpeercert.return_value = mock_cert
    mock_ssock.cipher.return_value = ('RC4-SHA', 'TLSv1', 128)
    mock_ssock.version.return_value = 'TLSv1'
    mock_ssock.__enter__.return_value = mock_ssock

    mock_context = MagicMock()
    mock_context.wrap_socket.return_value = mock_ssock

    monkeypatch.setattr(ssl, "create_default_context", lambda: mock_context)

    mock_sock = MagicMock()
    mock_sock.__enter__.return_value = mock_sock
    monkeypatch.setattr(socket, "create_connection", lambda address: mock_sock)

    import modules.ssl_analyzer as sa
    monkeypatch.setattr(sa, 'animated_progress_bar', lambda *a, **k: None)
    monkeypatch.setattr(sa, 'print_table', lambda *a, **k: None)
    monkeypatch.setattr(sa, 'print_status', lambda *a, **k: None)

    results = ssl_analyzer("https://example.com")
    result_dict = dict(results)

    vulns = result_dict["Vulnerabilities"]
    assert "POODLE" in vulns
    assert "RC4" in vulns
    assert "Expiring" in vulns

def test_ssl_analyzer_failure(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", MagicMock(side_effect=Exception("Connection failed")))

    import modules.ssl_analyzer as sa
    monkeypatch.setattr(sa, 'animated_progress_bar', lambda *a, **k: None)
    monkeypatch.setattr(sa, 'print_status', lambda *a, **k: None)

    results = ssl_analyzer("https://example.com")
    assert results == []
