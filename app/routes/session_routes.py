# session_routes.py
import qrcode
import io
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta, timezone
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

from .. import schemas

@router.post("/create-session")
def create_session(
    name: str,  # from query
    duration_minutes: int,
    gps_lat: float = None,
    gps_lon: float = None,
    allowed_radius: float = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    role = current_user.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create sessions")

    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(minutes=duration_minutes)

    new_session = models.AttendanceSession(
        title=name,
        start_time=start_time,
        end_time=end_time,
        created_by=current_user["user_id"],
        qr_code="",
        gps_lat=gps_lat,
        gps_lon=gps_lon,
        allowed_radius=allowed_radius
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    qr_data = {"session_id": new_session.session_id, "end_time": end_time.isoformat()}
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    new_session.qr_code = f"session_{new_session.session_id}.png"
    db.commit()

    return StreamingResponse(buf, media_type="image/png")
