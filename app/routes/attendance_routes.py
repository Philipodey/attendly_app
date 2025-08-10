# routes/attendance_routes.py
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.face_recognition import verify_face
from app.utils.gps_check import check_gps_location
from app.utils.vpn_check import is_vpn
from app.database import get_db
from app.models import User, AttendanceRecord, AttendanceSession
from datetime import datetime
import cv2
import numpy as np

router = APIRouter()

@router.post("/mark_attendance")
async def mark_attendance(
    session_id: int = Form(...),
    user_id: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: UploadFile = None,
    db: Session = Depends(get_db)
):
    try:
        # Retrieve user
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Retrieve session
        session = db.query(AttendanceSession).filter(AttendanceSession.session_id == session_id).first()
        if not session:
            raise ValueError("Session not found")

        # GPS location check
        try:
            check_gps_location(latitude, longitude, session.location_lat, session.location_long)
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"GPS check failed: {str(e)}")

        # VPN usage check
        try:
            is_vpn()
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"VPN check failed: {str(e)}")

        # Read image into OpenCV format
        image_bytes = await image.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Verify face
        match, score = verify_face(frame, user.face_embedding)
        if not match:
            raise HTTPException(status_code=403, detail=f"Face verification failed. Score: {score:.2f}")

        # Mark attendance
        record = db.query(AttendanceRecord).filter_by(session_id=session_id, user_id=user_id).first()
        if not record:
            record = AttendanceRecord(session_id=session_id, user_id=user_id, check_in_time=datetime.now())
            db.add(record)
        else:
            record.check_out_time = datetime.now()

        db.commit()
        return {"status": "success", "message": "Attendance marked", "match_score": score}

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
