from fastapi import FastAPI
from app.routes import attendance_routes, auth_routes, session_routes

app = FastAPI()

# Include routes
app.include_router(attendance_routes.router, prefix="/attendance", tags=["Attendance"])
app.include_router(auth_routes.router, prefix="/register", tags=["register"])
app.include_router(auth_routes.router, prefix="/login", tags=["login"])
app.include_router(auth_routes.router, prefix="/create-session", tags=["create_session"])


@app.get("/")
def root():
    return {"message": "Welcome to Attendly API"}
