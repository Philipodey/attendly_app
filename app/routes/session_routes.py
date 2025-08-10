# session_routes.py
import qrcode
import io
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth
from ..database import SessionLocal


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create-session")
def create_session(name: str, duration_minutes: int, user_id: int, db: Session = Depends(get_db)):
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)

    new_session = models.Session(
        name=name,
        expires_at=expires_at,
        created_by=user_id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Create QR code with session_id
    qr_data = {"session_id": new_session.session_id, "expires_at": expires_at.isoformat()}
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
