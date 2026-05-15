from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .models import RoleEnum

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.STUDENT

class UserOut(UserBase):
    id: int
    role: RoleEnum
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class SemesterCreate(BaseModel):
    name: str

class DepartmentCreate(BaseModel):
    name: str

class SubjectCreate(BaseModel):
    code: str
    name: str
    department_id: int
    is_lab: bool = False

class TeacherCreate(BaseModel):
    user_id: int
    department_id: int
    name: str

class StudentCreate(BaseModel):
    user_id: int
    department_id: int
    roll_number: str

class AllocationCreate(BaseModel):
    student_id: int
    subject_id: int
    semester_id: int

class ClassroomCreate(BaseModel):
    room_number: str
    capacity: int
    building: str

class TeacherSectionCreate(BaseModel):
    teacher_id: int
    subject_id: int
    semester_id: int
    name: str
    capacity: int

class TimetableSlotCreate(BaseModel):
    section_id: int
    day_of_week: int
    start_time: str
    end_time: str
    room_id: int

class TeacherSignup(BaseModel):
    email: str
    name: str
    department_id: int

class StudentSignup(BaseModel):
    email: str
    roll_number: str
    department_id: int
