from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.STUDENT)

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    roll_number = Column(String, unique=True, index=True)
    
    user = relationship("User")
    department = relationship("Department")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    name = Column(String)
    
    user = relationship("User")
    department = relationship("Department")

class Semester(Base):
    __tablename__ = "semesters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    selection_start = Column(DateTime, nullable=True)
    selection_end = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)
    is_portal_open = Column(Boolean, default=False)

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"))
    is_lab = Column(Boolean, default=False)

class StudentSubjectAllocation(Base):
    __tablename__ = "student_subject_allocations"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    
    student = relationship("Student")
    subject = relationship("Subject")
    semester = relationship("Semester")

class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True)
    capacity = Column(Integer)
    building = Column(String)
    is_lab = Column(Boolean, default=False)

class TeacherSection(Base):
    __tablename__ = "teacher_sections"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    name = Column(String)
    capacity = Column(Integer)
    
    teacher = relationship("Teacher")
    subject = relationship("Subject")
    timetable_slots = relationship("TimetableSlot", back_populates="section")

class TimetableSlot(Base):
    __tablename__ = "timetable_slots"
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("teacher_sections.id"))
    day_of_week = Column(Integer) # 0=Monday, 6=Sunday
    start_time = Column(String) # e.g. "08:00"
    end_time = Column(String) # e.g. "08:50" or "09:20"
    room_id = Column(Integer, ForeignKey("classrooms.id"))

    section = relationship("TeacherSection", back_populates="timetable_slots")
    room = relationship("Classroom")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    section_id = Column(Integer, ForeignKey("teacher_sections.id"))
    
    student = relationship("Student")
    section = relationship("TeacherSection")

class Waitlist(Base):
    __tablename__ = "waitlists"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    section_id = Column(Integer, ForeignKey("teacher_sections.id"))
    
    student = relationship("Student")
    section = relationship("TeacherSection")
    position = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
