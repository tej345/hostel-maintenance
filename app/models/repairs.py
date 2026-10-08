# app/models/repairs.py
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class RepairLog(Base):
    __tablename__ = "repair_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    complaint_id: Mapped[int] = mapped_column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), unique=True, nullable=False)
    technician_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)
    
    parts_replaced: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parts_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    labor_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Generated stored column handled automatically at database level
    total_cost: Mapped[float] = mapped_column(Numeric(10, 2), server_default="0.00")
    
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    complaint: Mapped["Complaint"] = relationship("Complaint")
    technician: Mapped["User"] = relationship("User")