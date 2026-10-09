# app/schemas/users.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.users import UserRoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: UserRoleEnum
    registration_number: Optional[str] = None
    room_id: Optional[int] = None

    class Config:
        from_attributes = True