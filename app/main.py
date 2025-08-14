from fastapi import FastAPI
from app.routes import attendance_routes, auth_routes, session_routes

app = FastAPI()

# Include routes
app.include_router(attendance_routes.router, prefix="/attendance", tags=["Attendance"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(session_routes.router, prefix="/sessions", tags=["Sessions"])

@app.get("/")
def root():
    return {"message": "Welcome to Attendly API"}
