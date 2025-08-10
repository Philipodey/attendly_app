from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    face_embedding = Column(String, nullable=False)
    matric_number = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    session_id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String, nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=False)
    qr_code = Column(String, nullable=False)
    gps_lat = Column(Float)
    gps_lon = Column(Float)
    allowed_radius = Column(Integer, default=100)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    record_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.session_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    check_in_time = Column(TIMESTAMP(timezone=True))
    check_out_time = Column(TIMESTAMP(timezone=True))
    gps_lat = Column(Float)
    gps_lon = Column(Float)
    vpn_detected = Column(Boolean, default=False)
    face_match_score = Column(Float)
    __table_args__ = (UniqueConstraint("session_id", "user_id", name="_user_session_uc"),)
