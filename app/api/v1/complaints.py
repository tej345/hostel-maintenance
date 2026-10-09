# app/api/v1/complaints.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.users import User, UserRoleEnum
from app.models.complaints import Complaint, StatusEnum
from app.models.repairs import RepairLog
from app.schemas.complaints import ComplaintCreate, ComplaintAssign, ComplaintResponse
from app.schemas.repairs import RepairLogCreate, RepairLogResponse
from app.core.deps import get_current_user, RoleChecker

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Students lodge a complaint
@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    payload: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRoleEnum.STUDENT]))
):
    if not current_user.room_id:
        raise HTTPException(status_code=400, detail="Student must be assigned to a room to raise a complaint")

    new_complaint = Complaint(
        title=payload.title,
        description=payload.description,
        category_id=payload.category_id,
        priority=payload.priority,
        student_id=current_user.id,
        room_id=current_user.room_id,
        status=StatusEnum.PENDING
    )
    db.add(new_complaint)
    await db.commit()
    await db.refresh(new_complaint)
    return new_complaint

# Get all complaints (Filtered by role)
@router.get("/", response_model=List[ComplaintResponse])
async def list_complaints(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Complaint)
    if current_user.role == UserRoleEnum.STUDENT:
        query = query.where(Complaint.student_id == current_user.id)
    elif current_user.role == UserRoleEnum.TECHNICIAN:
        query = query.where(Complaint.assigned_technician_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().all()

# Warden assigns a technician
@router.patch("/{complaint_id}/assign", response_model=ComplaintResponse)
async def assign_technician(
    complaint_id: int,
    payload: ComplaintAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRoleEnum.WARDEN, UserRoleEnum.ADMIN]))
):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.assigned_technician_id = payload.technician_id
    complaint.status = StatusEnum.ASSIGNED
    await db.commit()
    await db.refresh(complaint)
    return complaint

# Technician resolves complaint & logs costs
@router.post("/{complaint_id}/resolve", response_model=RepairLogResponse)
async def resolve_complaint(
    complaint_id: int,
    payload: RepairLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRoleEnum.TECHNICIAN, UserRoleEnum.ADMIN]))
):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    repair_log = RepairLog(
        complaint_id=complaint_id,
        technician_id=current_user.id,
        action_taken=payload.action_taken,
        parts_replaced=payload.parts_replaced,
        parts_cost=payload.parts_cost,
        labor_cost=payload.labor_cost
    )
    db.add(repair_log)
    await db.commit()
    await db.refresh(repair_log)
    return repair_log

@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalars().first()
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    # Ensure the user owns the complaint (or is an Admin)
    if complaint.student_id != current_user.id and current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this complaint")
        
    await db.delete(complaint)
    await db.commit()