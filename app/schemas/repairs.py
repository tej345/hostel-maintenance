# app/schemas/repairs.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RepairLogCreate(BaseModel):
    action_taken: str
    parts_replaced: Optional[str] = None
    parts_cost: float = Field(default=0.00, ge=0)
    labor_cost: float = Field(default=0.00, ge=0)

class RepairLogResponse(BaseModel):
    id: int
    complaint_id: int
    technician_id: int
    action_taken: str
    parts_replaced: Optional[str]
    parts_cost: float
    labor_cost: float
    total_cost: float
    logged_at: datetime

    class Config:
        from_attributes = True