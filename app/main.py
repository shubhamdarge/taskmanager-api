from fastapi import FastAPI, HTTPException
from app.routes import tasks
from app.auth import signup_email_password, login_email_password

app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="FastAPI + Supabase task manager with JWT auth and Swagger.",
)

@app.get("/", tags=["health"])
async def health():
    return {"status": "ok"}

@app.post("/auth/signup", tags=["auth"])
async def signup(email: str, password: str):
    try:
        res = await signup_email_password(email, password)
        # supabase-py v2 returns {user: {...}} shape on admin create
        uid = getattr(res.user, "id", None) if hasattr(res, "user") else None
        return {"id": uid, "email": email}
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.post("/auth/login", tags=["auth"])
async def login(email: str, password: str):
    try:
        res = await login_email_password(email, password)
        session = getattr(res, "session", None)
        if not session:
            raise ValueError("No session returned")
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
        }
    except Exception:
        raise HTTPException(401, detail="Invalid credentials")

app.include_router(tasks.router)
