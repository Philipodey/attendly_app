from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# =========================
# User Schemas
# =========================
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    matric_number: Optional[str] = None
    face_embedding: Optional[str] = None  # Optional for students during registration


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# =========================
# Token Schemas
# =========================
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# =========================
# Attendance Session Schemas
# =========================
class AttendanceSessionBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    allowed_radius: Optional[int] = 100


class AttendanceSessionCreate(AttendanceSessionBase):
    pass


class AttendanceSessionOut(AttendanceSessionBase):
    session_id: int
    created_by: int
    qr_code: str
    created_at: datetime

    class Config:
        orm_mode = True


# =========================
# Attendance Record Schemas
# =========================
class AttendanceRecordBase(BaseModel):
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    vpn_detected: Optional[bool] = False
    face_match_score: Optional[float] = None


class AttendanceRecordCreate(AttendanceRecordBase):
    session_id: int
    user_id: int
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None


class AttendanceRecordOut(AttendanceRecordBase):
    record_id: int
    session_id: int
    user_id: int
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]

    class Config:
        orm_mode = True
