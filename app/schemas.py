from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    done: Optional[bool] = None

class TaskOut(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: Optional[str] = None
    done: bool
    created_at: datetime
    updated_at: datetime
