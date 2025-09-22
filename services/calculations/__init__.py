import os
import importlib

# Automatically import all modules inside this folder
modules = [
    f[:-3] for f in os.listdir(os.path.dirname(__file__))
    if f.endswith(".py") and f not in ["__init__.py"]
]

for module_name in modules:
    module = importlib.import_module(f"services.calculations.{module_name}")
    globals().update({
        name: getattr(module, name) for name in dir(module)
        if not name.startswith("_")  # ignore private stuff
    })
