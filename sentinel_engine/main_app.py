# Wrapper that owns router composition without touching api.py
from .api import app                # your original app (guard, health, teams)
from .version_api import router_version

# If tenants router is defined in api.py or elsewhere it remains intact.
# We only add version here explicitly.
app.include_router(router_version)
