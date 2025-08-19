import importlib, sys
m = importlib.import_module("sentinel_engine.api")
print("OK: api loaded; has app =", hasattr(m, "app"))
