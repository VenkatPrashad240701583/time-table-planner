from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, admin, student, realtime, teacher

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Timetable System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(realtime.router)

@app.get("/")
def root():
    return FileResponse("templates/index.html")

@app.get("/admin-dashboard")
def admin_page():
    return FileResponse("templates/admin_dashboard.html")

@app.get("/admin-setup")
def admin_setup_page():
    return FileResponse("templates/admin_setup.html")

@app.get("/teacher-dashboard")
def teacher_page():
    return FileResponse("templates/teacher_dashboard.html")

@app.get("/profile")
def profile_page():
    return FileResponse("templates/profile.html")

@app.get("/student-dashboard")
def student_page():
    return FileResponse("templates/student_dashboard.html")

@app.get("/timetable-selection")
def select_page():
    return FileResponse("templates/timetable_selection.html")

