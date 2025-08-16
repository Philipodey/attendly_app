# app/routes/attendance_routes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Request
from sqlalchemy.orm import Session
from app.utils.face_recognition import verify_face
from app.utils.gps_check import check_gps_location
from app.utils.vpn_check import is_vpn
from app.database import get_db
from app.models import User, AttendanceRecord, AttendanceSession
from datetime import datetime
import numpy as np
import cv2

router = APIRouter()

@router.post("/mark_attendance")
async def mark_attendance(
    request: Request,
    session_id: int = Form(...),
    user_id: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # --- User
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # --- Session
    session = db.query(AttendanceSession).filter(AttendanceSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # --- GPS check (use correct fields: gps_lat/gps_lon/allowed_radius)
    if session.gps_lat is not None and session.gps_lon is not None and session.allowed_radius:
        inside = check_gps_location(
            float(latitude),
            float(longitude),
            float(session.gps_lat),
            float(session.gps_lon),
            radius_meters=int(session.allowed_radius)
        )
        if not inside:
            raise HTTPException(status_code=403, detail="You are outside the allowed attendance radius")

    # --- VPN check (best-effort; don’t block prototype if lookup fails)
    try:
        client_ip = request.client.host if request and request.client else ""
        if client_ip and is_vpn(client_ip):
            raise HTTPException(status_code=403, detail="VPN/Proxy usage detected")
    except Exception:
        pass

    # --- Decode uploaded image into OpenCV
    image_bytes = await image.read()
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # --- Face verification
    match, score = verify_face(frame, user.face_embedding)
    # Convert NumPy types (e.g., np.float32) to native Python float to avoid 500
    try:
        score = float(score) if score is not None else 0.0
    except Exception:
        score = 0.0

    if not match:
        raise HTTPException(status_code=403, detail=f"Face verification failed. Score: {score:.2f}")

    # --- Save attendance (toggle check-in/check-out)
    record = db.query(AttendanceRecord).filter_by(session_id=session_id, user_id=user_id).first()
    if not record:
        record = AttendanceRecord(
            session_id=int(session_id),
            user_id=int(user_id),
            check_in_time=datetime.utcnow(),
            gps_lat=float(latitude),
            gps_lon=float(longitude),
            face_match_score=score,
            vpn_detected=False
        )
        db.add(record)
    else:
        record.check_out_time = datetime.utcnow()
        record.gps_lat = float(latitude)
        record.gps_lon = float(longitude)
        record.face_match_score = score
        record.vpn_detected = False

    db.commit()

    # ✅ Return only native Python types
    return {
        "status": "success",
        "message": "Attendance marked",
        "match_score": score  # native float now
    }
