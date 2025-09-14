# Placeholder for shared dependencies (e.g., pagination params)
from typing import Optional
from fastapi import Query

def pagination(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    return {"limit": limit, "offset": offset}
