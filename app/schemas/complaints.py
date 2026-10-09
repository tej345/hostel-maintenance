# app/schemas/complaints.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.complaints import PriorityEnum, StatusEnum

class ComplaintCreate(BaseModel):
    title: str
    description: str
    category_id: int
    priority: PriorityEnum = PriorityEnum.MEDIUM

class ComplaintAssign(BaseModel):
    technician_id: int

class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    category_id: int
    student_id: int
    room_id: int
    priority: PriorityEnum
    status: StatusEnum
    assigned_technician_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True