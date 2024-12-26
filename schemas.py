import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, EmailStr
from sqlmodel import Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from models import TestData, CompletedCourses


class UserCreate(BaseModel):
    email: EmailStr = Field(default='Email')  # почта
    phone: PhoneNumber = Field(default='+78005553535')
    name: str = Field(default='Имя')  # имя
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class UserUpdate(BaseModel):
    email: EmailStr = Field(default='Email')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class CreateNewPassword(BaseModel):
    email: EmailStr = Field(default='Email')
    code: str = Field(default='Verify code')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class GetUser(BaseModel):
    email: EmailStr
    name: str


class GetUserForAdmin(BaseModel):
    id: Optional[int]
    role: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    name: Optional[str]
    date_reg: datetime


class AddCourse(BaseModel):
    title: str
    topic: str
    data: str


class AddUpdateCourse(BaseModel):
    data: str


class GetCourse(BaseModel):
    title: Optional[str] = Field(default=None)
    topic: Optional[str] = Field(default=None)
    offset: int = Field(default=0, description='offset')
    limit: int = Field(default=10, description='limit')


class CourseResponse(BaseModel):
    id: Optional[int]
    title: str
    topic: str
    date_create: datetime
    date_last_update: datetime


class AddTest(BaseModel):
    title: str
    topic: str
    data: List[TestData]


class ReadTestSearch(BaseModel):
    id: Optional[int]
    courses_id: int
    title: str
    topic: str
    date_create: datetime
    date_last_update: datetime


class ReadTestResponse(BaseModel):
    id: Optional[int]
    courses_id: int
    title: str
    topic: str
    exercise: str
    date_create: datetime
    date_last_update: datetime


class AddUpdateTest(BaseModel):
    data: TestData


class GetTestByName(BaseModel):
    title: Optional[str] = Field(default=None)
    topic: Optional[str] = Field(default=None)
    offset: int = Field(default=0, description='offset')
    limit: int = Field(default=10, description='limit')


class GetTestByCourse(BaseModel):
    offset: int = Field(default=0, description='offset')
    limit: int = Field(default=10, description='limit')


class AnswerTest(BaseModel):
    answer: str


class AddVideo(BaseModel):
    course_id: int
    title: Optional[str] = Field(default='Video tutorial', max_length=255)
    topic: Optional[str] = Field(default='topic', max_length=255)


class UpdateVideo(BaseModel):
    title: Optional[str] = Field(default='Video tutorial', max_length=255)


class GetVideoByName(BaseModel):
    title: Optional[str] = Field(default=None)
    topic: Optional[str] = Field(default=None)
    offset: int = Field(default=0, description='offset')
    limit: int = Field(default=10, description='limit')


class GetVideoByCourse(BaseModel):
    course_id: int
    offset: int = Field(default=0, description='offset')
    limit: int = Field(default=10, description='limit')


class ReturnVideoSearch(BaseModel):
    course_id: int
    title: str
    topic: str
    date_create: datetime
    date_last_update: datetime


class MessageCreate(BaseModel):
    sender_user_id: int
    recipient_user_id: int
    message: str


class MessageResponse(BaseModel):
    id: int
    sender_user_id: int
    recipient_user_id: int
    message: str
    date_create: datetime
    date_last_update: datetime


class CreateUpdateMessage(BaseModel):
    recipient_user_id: int
    message: str = Field(default='message')


class Email(BaseModel):
    email: str