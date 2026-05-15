import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..dependencies import get_current_student_user
from .realtime import broadcast_event

router = APIRouter(prefix="/api/student", tags=["student"])

@router.get("/portal-status")
def get_portal_status(db: Session = Depends(get_db)):
    active_semester = db.query(models.Semester).filter(models.Semester.is_active == True).first()
    if not active_semester:
        return {"is_open": False}
    return {"is_open": active_semester.is_portal_open}

@router.get("/sections")
def get_available_sections(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_student_user)):
    student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
    active_semester = db.query(models.Semester).filter(models.Semester.is_active == True).first()
    if not student or not active_semester:
        return []
        
    allocations = db.query(models.StudentSubjectAllocation).filter(
        models.StudentSubjectAllocation.student_id == student.id,
        models.StudentSubjectAllocation.semester_id == active_semester.id
    ).all()
    subject_ids = [a.subject_id for a in allocations]
    
    sections = db.query(models.TeacherSection).filter(
        models.TeacherSection.semester_id == active_semester.id,
        models.TeacherSection.subject_id.in_(subject_ids)
    ).all()
    
    result = []
    for sec in sections:
        enrolled_count = db.query(models.Enrollment).filter(models.Enrollment.section_id == sec.id).count()
        slots = db.query(models.TimetableSlot).filter(models.TimetableSlot.section_id == sec.id).all()
        is_enrolled = db.query(models.Enrollment).filter(models.Enrollment.section_id == sec.id, models.Enrollment.student_id == student.id).first() is not None
        result.append({
            "id": sec.id,
            "subject": sec.subject.name,
            "teacher": sec.teacher.name,
            "capacity": sec.capacity,
            "enrolled": enrolled_count,
            "is_enrolled": is_enrolled,
            "slots": [{"day": s.day_of_week, "start": s.start_time, "end": s.end_time} for s in slots]
        })
    return result

@router.post("/enroll")
async def enroll_section(section_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_student_user)):
    student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
    active_semester = db.query(models.Semester).filter(models.Semester.is_active == True).first()
    if not active_semester or not active_semester.is_portal_open:
        raise HTTPException(status_code=403, detail="Portal is closed")
        
    section = db.query(models.TeacherSection).filter(models.TeacherSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    existing_enrollments = db.query(models.Enrollment).join(models.TeacherSection).filter(
        models.Enrollment.student_id == student.id,
        models.TeacherSection.subject_id == section.subject_id,
        models.TeacherSection.semester_id == active_semester.id
    ).first()
    if existing_enrollments:
        raise HTTPException(status_code=400, detail="Already enrolled in this subject")
        
    my_enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == student.id).all()
    my_section_ids = [e.section_id for e in my_enrollments]
    my_slots = db.query(models.TimetableSlot).filter(models.TimetableSlot.section_id.in_(my_section_ids)).all()
    
    new_slots = db.query(models.TimetableSlot).filter(models.TimetableSlot.section_id == section_id).all()
    
    for ns in new_slots:
        for ms in my_slots:
            if ns.day_of_week == ms.day_of_week:
                if (ns.start_time < ms.end_time) and (ns.end_time > ms.start_time):
                    raise HTTPException(status_code=400, detail="Timetable clash detected")
                    
    enrolled_count = db.query(models.Enrollment).filter(models.Enrollment.section_id == section_id).count()
    if enrolled_count >= section.capacity:
        pos = db.query(models.Waitlist).filter(models.Waitlist.section_id == section_id).count() + 1
        wl = models.Waitlist(student_id=student.id, section_id=section_id, position=pos)
        db.add(wl)
        db.commit()
        await broadcast_event(json.dumps({"type": "waitlist_update", "section_id": section_id, "count": pos}))
        return {"message": "Added to waitlist", "position": pos}
        
    enrollment = models.Enrollment(student_id=student.id, section_id=section_id)
    db.add(enrollment)
    db.commit()
    
    await broadcast_event(json.dumps({"type": "seat_update", "section_id": section_id, "enrolled": enrolled_count + 1}))
    return {"message": "Enrolled successfully"}

@router.delete("/unenroll")
async def unenroll_section(section_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_student_user)):
    student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
    active_semester = db.query(models.Semester).filter(models.Semester.is_active == True).first()
    if not active_semester or not active_semester.is_portal_open:
        raise HTTPException(status_code=403, detail="Portal is closed")
        
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == student.id,
        models.Enrollment.section_id == section_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    db.delete(enrollment)
    db.commit()
    
    enrolled_count = db.query(models.Enrollment).filter(models.Enrollment.section_id == section_id).count()
    await broadcast_event(json.dumps({"type": "seat_update", "section_id": section_id, "enrolled": enrolled_count}))
    return {"message": "Unenrolled successfully"}
