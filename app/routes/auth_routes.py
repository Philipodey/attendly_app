from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import EmailStr
import numpy as np
import cv2

from .. import models, auth, schemas
from ..database import SessionLocal
from ..utils.face_recognition import generate_face_embedding  # Custom function

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=schemas.Token)
def register(
    full_name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    matric_number: str = Form(None),
    face_image: UploadFile = File(None),  # Optional
    db: Session = Depends(get_db)
):
    role = role.lower().strip()

    # --- Check duplicates ---
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if matric_number and db.query(models.User).filter(models.User.matric_number == matric_number).first():
        raise HTTPException(status_code=400, detail="Matric number already registered")

    # --- Hash password ---
    hashed_pw = auth.hash_password(password)

    embedding_str = None

    if role in ["student", "employee"]:
        if not face_image:
            raise HTTPException(status_code=400, detail="Face image is required for students and employees")

        # Read image
        image_bytes = face_image.file.read()
        np_image = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image uploaded")

        # Generate embedding
        try:
            embedding_str = generate_face_embedding(img)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    else:
        embedding_str = "NO FACE"
    # --- Save user ---
    new_user = models.User(
        full_name=full_name,
        email=email,
        password_hash=hashed_pw,
        role=role,
        matric_number=matric_number,
        face_embedding=embedding_str
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Token
    access_token = auth.create_access_token(data={
        "sub": str(new_user.user_id),
        "user_id": new_user.user_id,
        "role": new_user.role

        })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user,
        "user_id": new_user.user_id,
        "role":new_user.role
    }

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = auth.create_access_token(data={
        "sub": str(user.user_id),
        "user_id": user.user_id,
        "role": user.role
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "user_id": user.user_id,       # ✅ include this
        "role": user.role  

    }
