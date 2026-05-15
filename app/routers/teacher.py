from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..dependencies import get_current_teacher_user

router = APIRouter(prefix="/api/teacher", tags=["teacher"])

@router.get("/schedule")
def get_teacher_schedule(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher_user)):
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
        
    sections = db.query(models.TeacherSection).filter(models.TeacherSection.teacher_id == teacher.id).all()
    
    schedule = []
    for sec in sections:
        slots = db.query(models.TimetableSlot).filter(models.TimetableSlot.section_id == sec.id).all()
        for slot in slots:
            schedule.append({
                "section_id": sec.id,
                "subject": sec.subject.name,
                "section_name": sec.name,
                "day": slot.day_of_week,
                "start": slot.start_time,
                "end": slot.end_time,
                "room": slot.room.room_number if slot.room else "TBA"
            })
            
    return schedule

@router.get("/sections/{section_id}/students")
def get_enrolled_students(section_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher_user)):
    teacher = db.query(models.Teacher).filter(models.Teacher.user_id == current_user.id).first()
    section = db.query(models.TeacherSection).filter(models.TeacherSection.id == section_id, models.TeacherSection.teacher_id == teacher.id).first()
    
    if not section:
        raise HTTPException(status_code=403, detail="Not authorized to view this section")
        
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.section_id == section.id).all()
    students = []
    for e in enrollments:
        students.append({
            "roll_number": e.student.roll_number,
            "email": e.student.user.email
        })
    return students
