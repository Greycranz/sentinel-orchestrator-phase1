from fastapi import FastAPI
from sentinel_engine.api import router as api_router
from sentinel_engine.orchestrator import startup_event, shutdown_event
from sentinel_engine.middleware import TimingAndAuthMiddleware
from sentinel_engine.db_extra import init_extra_tables, seed_default_teams

app = FastAPI(title="Sentinel Engine Orchestrator – Phase 4.1 (Free Mode + Teams)")

app.add_middleware(TimingAndAuthMiddleware)
app.include_router(api_router)

@app.on_event("startup")
async def _startup():
    init_extra_tables()
    seed_default_teams()
    await startup_event()

@app.on_event("shutdown")
async def _shutdown():
    await shutdown_event()
