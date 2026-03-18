import os
import sys
import pkgutil
import importlib
import pytest
from unittest.mock import MagicMock, patch

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.plugin_loader import load_plugins

def test_load_plugins_success(monkeypatch):
    # Mock pkgutil.iter_modules
    def mock_iter_modules(path):
        return [(None, "test_plugin", False)]
    monkeypatch.setattr(pkgutil, "iter_modules", mock_iter_modules)

    # Mock importlib.import_module
    mock_module = MagicMock()
    mock_module.run = lambda x: {"status": "ok"}
    mock_module.__name__ = "plugins.test_plugin"

    def mock_import_module(name):
        if name == "plugins.test_plugin":
            return mock_module
        raise ImportError()
    monkeypatch.setattr(importlib, "import_module", mock_import_module)

    # Mock os.path.exists and Path.exists
    from pathlib import Path
    monkeypatch.setattr(Path, "exists", lambda self: True)

    # Mock print_status
    import modules.plugin_loader as pl
    monkeypatch.setattr(pl, 'print_status', lambda *a, **k: None)

    plugins = load_plugins()

    assert len(plugins) == 1
    assert plugins[0].run("test") == {"status": "ok"}

def test_load_plugins_missing_run(monkeypatch):
    def mock_iter_modules(path):
        return [(None, "bad_plugin", False)]
    monkeypatch.setattr(pkgutil, "iter_modules", mock_iter_modules)

    mock_module = MagicMock(spec=[]) # No run attribute
    monkeypatch.setattr(importlib, "import_module", lambda name: mock_module)

    from pathlib import Path
    monkeypatch.setattr(Path, "exists", lambda self: True)

    import modules.plugin_loader as pl
    monkeypatch.setattr(pl, 'print_status', lambda *a, **k: None)

    plugins = load_plugins()
    assert len(plugins) == 0

def test_load_plugins_dir_not_found(monkeypatch):
    from pathlib import Path
    monkeypatch.setattr(Path, "exists", lambda self: False)

    plugins = load_plugins("nonexistent")
    assert plugins == []
