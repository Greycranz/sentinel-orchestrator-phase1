from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os, json

from .teams_api import router_teams
router = APIRouter()
router.include_router(router_teams)

@router.get("/tools/registry")
def get_tool_registry():
    path = os.path.join(os.path.dirname(__file__), "tool_registry.json")
    if not os.path.exists(path):
        return JSONResponse({"tools": []})
    with open(path, "r", encoding="utf-8") as f:
        return JSONResponse(json.load(f))

@router.post("/tools/registry")
def update_tool_registry(payload: dict):
    path = os.path.join(os.path.dirname(__file__), "tool_registry.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return {"ok": True}
