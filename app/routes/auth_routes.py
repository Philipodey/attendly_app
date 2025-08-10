from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth, schemas
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if matric_number exists (only if provided)
    if user_data.matric_number and db.query(models.User).filter(models.User.matric_number == user_data.matric_number).first():
        raise HTTPException(status_code=400, detail="Matric number already registered")

    hashed_pw = auth.hash_password(user_data.password)

    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_pw,
        role=user_data.role,
        matric_number=user_data.matric_number,
        face_embedding=user_data.face_embedding
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = auth.create_access_token(data={"sub": str(new_user.user_id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = auth.create_access_token(data={"sub": str(user.user_id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
