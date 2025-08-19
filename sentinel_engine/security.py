from fastapi import HTTPException, Request, status
import os

def _get_expected_key() -> str | None:
    # Launcher exports SENTINEL_API_KEY from .env before starting the app
    # (no python-dotenv needed here)
    return os.getenv("SENTINEL_API_KEY")

async def verify_api_key(request: Request) -> None:
    """
    Global guard used by middleware:
      - Accepts either X-API-Key: <key>
      - Or Authorization: Bearer <key>
    Raises 401 if missing or mismatched.
    """
    expected = _get_expected_key()
    if not expected:
        # Hard fail if the server is misconfigured
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Server missing SENTINEL_API_KEY")

    # Prefer explicit header; fall back to bearer
    provided = request.headers.get("x-api-key")
    if not provided:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            provided = auth.split(" ", 1)[1].strip()

    if not provided or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
# --- Compatibility shim ---
# Some legacy routes import guard_api_key instead of verify_api_key
# Keep signature identical so middleware & routes can both call it.
async def guard_api_key(request):
    return await verify_api_key(request)
