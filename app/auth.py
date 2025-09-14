from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client
from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

def supabase_public() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

def supabase_admin() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = creds.credentials
    try:
        user_res = supabase_public().auth.get_user(token)
        user = getattr(user_res, "user", None)
        if not user or not getattr(user, "id", None):
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user.id, "token": token}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- existing helpers for signup/login (keep as-is, but you can mark email confirmed for dev) ---

def supabase_client_admin() -> Client:
    return supabase_admin()

async def signup_email_password(email: str, password: str):
    admin = supabase_admin()
    # For dev convenience: mark email as confirmed
    return admin.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True
    })

async def login_email_password(email: str, password: str):
    # public client is fine for password login
    return supabase_public().auth.sign_in_with_password({"email": email, "password": password})
