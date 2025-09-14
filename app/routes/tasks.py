from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
from supabase import create_client
from app.schemas import TaskCreate, TaskUpdate, TaskOut
from app.auth import get_current_user, sb_public
from app.config import settings

router = APIRouter(prefix="/tasks", tags=["tasks"])
sb = sb_public  # RLS-enforced

@router.post("", response_model=TaskOut, status_code=201)
async def create_task(payload: TaskCreate, user=Depends(get_current_user)):
    values = {
        "title": payload.title,
        "description": payload.description,
        "owner_id": user["user_id"],
    }
    res = sb.table("tasks").insert(values).execute()
    if not res.data:
        raise HTTPException(400, "Could not create task")
    return res.data[0]

@router.get("", response_model=List[TaskOut])
async def list_tasks(
    done: Optional[bool] = Query(default=None, description="Filter by completion"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
):
    q = sb.table("tasks").select("*").order("created_at", desc=True)
    if done is not None:
        q = q.eq("done", done)
    if offset:
        q = q.range(offset, offset + limit - 1)
    else:
        q = q.range(0, limit - 1)
    res = q.execute()
    return res.data or []

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: UUID, user=Depends(get_current_user)):
    res = sb.table("tasks").select("*").eq("id", str(task_id)).single().execute()
    if not res.data:
        raise HTTPException(404, "Task not found")
    return res.data

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: UUID, payload: TaskUpdate, user=Depends(get_current_user)):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(400, "No fields to update")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    res = sb.table("tasks").update(updates).eq("id", str(task_id)).execute()
    if not res.data:
        raise HTTPException(404, "Task not found or not allowed")
    return res.data[0]

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID, user=Depends(get_current_user)):
    sb.table("tasks").delete().eq("id", str(task_id)).execute()
    return None
