from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..dependencies import get_current_admin_user
from ..core.security import get_password_hash

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/semester", response_model=dict)
def create_semester(semester: schemas.SemesterCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    new_semester = models.Semester(name=semester.name, is_active=True, is_portal_open=False)
    # optionally set other semesters to inactive
    db.query(models.Semester).update({models.Semester.is_active: False})
    db.add(new_semester)
    db.commit()
    return {"message": "Semester created successfully"}

@router.post("/department", response_model=dict)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    existing = db.query(models.Department).filter(models.Department.name == dept.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")
    new_dept = models.Department(name=dept.name)
    db.add(new_dept)
    db.commit()
    return {"message": "Department created"}

@router.post("/subject", response_model=dict)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    existing = db.query(models.Subject).filter(models.Subject.code == subject.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")
    new_subject = models.Subject(**subject.dict())
    db.add(new_subject)
    db.commit()
    return {"message": "Subject created"}

@router.post("/teacher", response_model=dict)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    new_teacher = models.Teacher(**teacher.dict())
    db.add(new_teacher)
    db.commit()
    return {"message": "Teacher profile created"}

@router.post("/signup-teacher", response_model=dict)
def signup_teacher(data: schemas.TeacherSignup, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash("password")
    new_user = models.User(email=data.email, password_hash=hashed_password, role=models.RoleEnum.TEACHER)
    db.add(new_user)
    db.flush() # Get user id
    
    new_teacher = models.Teacher(user_id=new_user.id, department_id=data.department_id, name=data.name)
    db.add(new_teacher)
    db.commit()
    return {"message": "Teacher user and profile created"}

@router.post("/signup-student", response_model=dict)
def signup_student(data: schemas.StudentSignup, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash("password")
    new_user = models.User(email=data.email, password_hash=hashed_password, role=models.RoleEnum.STUDENT)
    db.add(new_user)
    db.flush()
    
    new_student = models.Student(user_id=new_user.id, department_id=data.department_id, roll_number=data.roll_number)
    db.add(new_student)
    db.commit()
    return {"message": "Student user and profile created"}

@router.post("/student", response_model=dict)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    return {"message": "Student profile created"}

@router.post("/allocation", response_model=dict)
def allocate_subject(alloc: schemas.AllocationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    new_alloc = models.StudentSubjectAllocation(**alloc.dict())
    db.add(new_alloc)
    db.commit()
    return {"message": "Subject allocated to student"}

@router.post("/classroom", response_model=dict)
def create_classroom(classroom: schemas.ClassroomCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    new_classroom = models.Classroom(**classroom.dict())
    db.add(new_classroom)
    db.commit()
    return {"message": "Classroom created"}

@router.post("/teacher-section", response_model=dict)
def create_teacher_section(section: schemas.TeacherSectionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    new_section = models.TeacherSection(**section.dict())
    db.add(new_section)
    db.commit()
    return {"message": "Teacher section created"}

@router.post("/timetable-slot", response_model=dict)
def create_timetable_slot(slot: schemas.TimetableSlotCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    new_slot = models.TimetableSlot(**slot.dict())
    db.add(new_slot)
    db.commit()
    return {"message": "Timetable slot created"}


@router.post("/semester/reset", response_model=dict)
def reset_semester(semester_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    """Deletes all timetable allocations for a semester, forcing students to redo."""
    db.query(models.Enrollment).filter(
        models.Enrollment.section_id.in_(
            db.query(models.TeacherSection.id).filter(models.TeacherSection.semester_id == semester_id)
        )
    ).delete(synchronize_session=False)
    db.query(models.Waitlist).filter(
        models.Waitlist.section_id.in_(
            db.query(models.TeacherSection.id).filter(models.TeacherSection.semester_id == semester_id)
        )
    ).delete(synchronize_session=False)
    db.commit()
    return {"message": "Semester allocations reset successfully"}

@router.put("/semester/{semester_id}/toggle-portal", response_model=dict)
def toggle_portal(semester_id: int, is_open: bool, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    semester = db.query(models.Semester).filter(models.Semester.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    semester.is_portal_open = is_open
    db.commit()
    # Trigger global SSE update here eventually
    return {"message": f"Portal {'opened' if is_open else 'closed'}"}

@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    users_count = db.query(models.User).count()
    semesters = db.query(models.Semester).all()
    departments = db.query(models.Department).all()
    subjects = db.query(models.Subject).all()
    teachers = db.query(models.Teacher).all()
    students = db.query(models.Student).all()
    users = db.query(models.User).all()
    sections = db.query(models.TeacherSection).all()
    classrooms = db.query(models.Classroom).all()
    return {
        "users_count": users_count,
        "semesters": [{"id": s.id, "name": s.name, "is_portal_open": s.is_portal_open} for s in semesters],
        "departments": [{"id": d.id, "name": d.name} for d in departments],
        "subjects": [{"id": s.id, "name": s.name, "code": s.code} for s in subjects],
        "teachers": [{"id": t.id, "name": t.name, "user_id": t.user_id} for t in teachers],
        "students": [{"id": s.id, "roll_number": s.roll_number, "user_id": s.user_id} for s in students],
        "users": [{"id": u.id, "email": u.email, "role": u.role} for u in users],
        "sections": [{"id": s.id, "name": s.name, "teacher_id": s.teacher_id} for s in sections],
        "classrooms": [{"id": c.id, "room_number": c.room_number} for c in classrooms]
    }
