from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
import httpx
from app.config import settings
from supabase import create_client, Client

bearer_scheme = HTTPBearer(auto_error=False)

# Public client for table-level ops (RLS enforced)
sb_public: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# Cache JWKS in memory
_jwks_cache: Optional[dict] = None

async def _get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(settings.SUPABASE_JWKS_URL)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = creds.credentials
    jwks = await _get_jwks()

    # Find key by kid
    unverified = jwt.get_unverified_header(token)
    kid = unverified.get("kid")
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token (kid)")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            options={"verify_aud": False},
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": payload.get("sub")}

# Optional helpers for sign-up / sign-in (server-only / demo)
def supabase_client_admin() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

async def signup_email_password(email: str, password: str):
    admin = supabase_client_admin()
    return admin.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True  # <-- mark as confirmed
    })

async def login_email_password(email: str, password: str):
    # Client-side auth is recommended; shown here for completeness.
    return sb_public.auth.sign_in_with_password({"email": email, "password": password})
