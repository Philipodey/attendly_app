from pydantic import BaseModel, EmailStr
from typing import Optional


# Request schemas
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    matric_number: Optional[str] = None  # Optional for admins, required for students
    face_embedding: Optional[str] = None  # Stored string from DeepFace


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Response schemas
class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    role: str
    matric_number: Optional[str] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
