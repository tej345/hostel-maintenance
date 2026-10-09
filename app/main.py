# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select

from app.database import engine, Base, AsyncSessionLocal
from app.core.security import hash_password
from app.models.users import User, UserRoleEnum
from app.api.v1 import auth, complaints
from sqlalchemy.future import select
from sqlalchemy import text # 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Auto-Migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Auto-Seeding
    async with AsyncSessionLocal() as session:
        query = select(User).where(User.email == "arjun.k2022@vitchennai.ac.in")
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            test_student = User(
                full_name="Arjun K",                          # Required by String(100), nullable=False
                email="arjun.k2022@vitchennai.ac.in",
                phone="9876543210",                           # Required by String(15), nullable=False
                password_hash=hash_password("admin123"),      # Corrected field name & hashing function
                role=UserRoleEnum.STUDENT,                    # Using the strict Enum class
                registration_number="22BCE1234"               # Required by CheckConstraint chk_student_reg_no
            )
            session.add(test_student)
            await session.commit()
            print("Successfully seeded test student: arjun.k2022@vitchennai.ac.in")

            # 3. Seed Default Infrastructure (Blocks, Rooms, Categories)
            await session.execute(text("""
                INSERT INTO blocks (block_name, gender, total_floors, has_ac) 
                VALUES ('Men Hostel A', 'MALE', 6, false) 
                ON CONFLICT (block_name) DO NOTHING;
            """))
            await session.execute(text("""
                INSERT INTO rooms (block_id, room_number, floor_number, room_type) 
                VALUES (1, '101', 1, '2 Bed') 
                ON CONFLICT (block_id, room_number) DO NOTHING;
            """))
            await session.execute(text("""
                INSERT INTO complaint_categories (name, description) 
                VALUES ('Plumbing', 'Water leaks, broken taps, pipes') 
                ON CONFLICT (name) DO NOTHING;
            """))
            
            await session.execute(text("""
                UPDATE users SET room_id = 1 WHERE email = 'arjun.k2022@vitchennai.ac.in';
            """))
            
            await session.commit()
            print("Successfully seeded infrastructure and assigned room to student.")

    yield

app = FastAPI(
    title="VIT Chennai Hostel Maintenance Tracker API",
    version="1.0.0",
    description="Backend API for managing hostel complaints, technician assignments, and repair audits.",
    lifespan=lifespan
)

# Enable CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(complaints.router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "online", "message": "VIT Chennai Hostel Maintenance API is running"}