# app/models/infrastructure.py
import enum
from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    block_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    gender: Mapped[GenderEnum] = mapped_column(SQLEnum(GenderEnum, name="gender_type"), nullable=False)
    total_floors: Mapped[int] = mapped_column(Integer, nullable=False)
    has_ac: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="block", cascade="all, delete-orphan")

class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint("block_id", "room_number", name="uq_block_room"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    room_number: Mapped[str] = mapped_column(String(10), nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    block: Mapped["Block"] = relationship("Block", back_populates="rooms")
    users: Mapped[List["User"]] = relationship("User", back_populates="room")