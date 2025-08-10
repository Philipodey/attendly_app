# routes/admin_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, AttendanceRecord, AttendanceSession
from datetime import date, datetime
from sqlalchemy import func

router = APIRouter()

@router.get("/dashboard/summary")
def get_attendance_summary(db: Session = Depends(get_db)):
    try:
        today = date.today()

        # Total students/employees present today
        total_present = db.query(AttendanceRecord).filter(
            func.date(AttendanceRecord.check_in_time) == today
        ).count()

        # List of all students with check-in and check-out times
        present_list = db.query(
            User.full_name,
            User.matric_number,
            AttendanceRecord.check_in_time,
            AttendanceRecord.check_out_time
        ).join(User, User.user_id == AttendanceRecord.user_id).filter(
            func.date(AttendanceRecord.check_in_time) == today
        ).all()

        # Attendance by session
        session_attendance = db.query(
            AttendanceSession.session_name,
            func.count(AttendanceRecord.record_id).label("count")
        ).join(AttendanceRecord, AttendanceSession.session_id == AttendanceRecord.session_id).filter(
            func.date(AttendanceRecord.check_in_time) == today
        ).group_by(AttendanceSession.session_name).all()

        return {
            "date": today.isoformat(),
            "total_present": total_present,
            "present_list": [
                {
                    "name": name,
                    "matric_number": matric,
                    "check_in": check_in.strftime("%H:%M:%S") if check_in else None,
                    "check_out": check_out.strftime("%H:%M:%S") if check_out else None
                }
                for name, matric, check_in, check_out in present_list
            ],
            "attendance_by_session": [
                {"session_name": sname, "count": count}
                for sname, count in session_attendance
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/analytics")
def get_attendance_analytics(db: Session = Depends(get_db)):
    try:
        total_students = db.query(User).count()
        total_records = db.query(AttendanceRecord).count()
        last_7_days = db.query(
            func.date(AttendanceRecord.check_in_time),
            func.count(AttendanceRecord.record_id)
        ).group_by(func.date(AttendanceRecord.check_in_time)).order_by(
            func.date(AttendanceRecord.check_in_time).desc()
        ).limit(7).all()

        return {
            "total_students": total_students,
            "total_attendance_records": total_records,
            "last_7_days": [
                {"date": d.isoformat(), "count": c} for d, c in last_7_days
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
