from fastapi import APIRouter, Depends
from sentinel_engine.security import guard_api_key
from sentinel_engine.keys import rotate_key
from sentinel_engine.llm import detect_providers

router = APIRouter()

@router.post("/rotate-key")
def rotate(_: bool = Depends(guard_api_key)):
    new = rotate_key()
    return {"ok": True, "new_key_preview": f"{new[:4]}...{new[-4:]}"}

@router.get("/llm/providers")
def providers(_: bool = Depends(guard_api_key)):
    det = detect_providers()
    return {"providers": [dict(name=p.name, keys_present=p.keys_present, details=p.details) for p in det]}
