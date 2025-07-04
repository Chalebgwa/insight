import importlib
import pkgutil
from pathlib import Path
from .print_status import print_status


def load_plugins(path="plugins"):
    """Discover and load plugins with a run() function"""
    plugins = []
    plugins_dir = Path(path)
    if not plugins_dir.exists():
        return plugins

    for _, name, _ in pkgutil.iter_modules([str(plugins_dir)]):
        try:
            module = importlib.import_module(f"{plugins_dir.name}.{name}")
            if hasattr(module, "run") and callable(module.run):
                plugins.append(module)
                print_status(f"Loaded plugin: {name}", "success")
            else:
                print_status(f"Plugin {name} missing run()", "error")
        except Exception as e:
            print_status(f"Failed to load plugin {name}: {e}", "error")
    return plugins
