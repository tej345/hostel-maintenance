# app/models/users.py
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class UserRoleEnum(str, enum.Enum):
    STUDENT = "STUDENT"
    WARDEN = "WARDEN"
    TECHNICIAN = "TECHNICIAN"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "(role = 'STUDENT' AND registration_number IS NOT NULL) OR (role != 'STUDENT')",
            name="chk_student_reg_no"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(
        SQLEnum(UserRoleEnum, name="user_role"),
        nullable=False,
        default=UserRoleEnum.STUDENT
    )

    registration_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    room_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    room: Mapped[Optional["Room"]] = relationship("Room", back_populates="users")