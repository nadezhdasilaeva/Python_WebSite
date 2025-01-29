import json

from pydantic import BaseModel
from sqlalchemy import Column
from sqlmodel import SQLModel, Field, JSON
from typing import Optional, List
from datetime import datetime
from hashlib import sha256
from cryptography.fernet import Fernet
from config import SECRET_KEY


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    hash_password: str  # хэш пароля
    role: str = Field(default='user')  # роль пользователя super_user, teacher, user, BAN
    email: str  # почта
    phone: str
    name: str  # имя
    date_reg: datetime = Field(default=datetime.utcnow())  # дата регистрации
    temp_data: str = Field(nullable=True)

    def verify_password(self, password: str):
        return self.hash_password == sha256(password.encode()).hexdigest()

    def ban_user(self):
        self.role = 'BAN'

    def super_user(self):
        self.role = 'super_user'

    def user_user(self):
        self.role = 'user'

    def teacher_user(self):
        self.role = 'teacher'


class CompletedCourses(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key='user.id')
    course_id: int = Field(foreign_key='course.id')
    title: str
    topic: str
    data_completion_course: datetime = Field(default=datetime.utcnow())


class FavouritesCourse(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key='user.id')
    course_id: int = Field(foreign_key='course.id')
    title: str
    topic: str


class Avatar(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key='user.id')
    image: bytes = Field(nullable=False)

    def update_avatar(self, image: bytes):
        self.image = image


class Course(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str = Field(default='title')
    topic: str = Field(default='topic')
    data: str = Field(default='data')
    date_create: datetime = Field(default=datetime.utcnow())
    date_last_update: datetime = Field(default=datetime.utcnow())

    def update_data(self, data: str):
        self.data = data
        self.date_last_update = datetime.utcnow()


class Video(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    course_id: int = Field(foreign_key='course.id')
    title: str = Field(default='Video tutorial')
    topic: str = Field(default='topic')
    file_path: str
    content_type: str
    date_create: datetime = Field(default=datetime.utcnow())
    date_last_update: datetime = Field(default=datetime.utcnow())

    def update_title(self, title: str):
        self.title = title
        self.date_last_update = datetime.utcnow()


class TestData(BaseModel):
    exercise: str
    true_answer: str


class Test(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    courses_id: int = Field(foreign_key='course.id')
    title: str
    topic: str = Field(default='topic')
    data: List[TestData] = Field(sa_column=Column(JSON))
    date_create: datetime = Field(default=datetime.utcnow())
    date_last_update: datetime = Field(default=datetime.utcnow())

    def update_data(self, data: TestData):
        self.data = data
        self.date_last_update = datetime.utcnow()


class PracticeData(BaseModel):
    exercise: str
    true_answer: str


class Practice(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    courses_id: int = Field(foreign_key='course.id')
    title: str
    topic: str = Field(default='topic')
    data: List[PracticeData] = Field(sa_column=Column(JSON))
    date_create: datetime = Field(default=datetime.utcnow())
    date_last_update: datetime = Field(default=datetime.utcnow())

    def update_data(self, data: PracticeData):
        self.data = data
        self.date_last_update = datetime.utcnow()


class Message(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    sender_user_id: int = Field(foreign_key='user.id')
    recipient_user_id: int = Field(foreign_key='user.id')
    enc_message: bytes
    date_create: datetime = Field(default=datetime.utcnow())
    date_last_update: datetime = Field(default=datetime.utcnow())
    changed: bool = Field(default=False)

    def Update_data(self, message: str):
        key = Fernet(self.sender_user_id + SECRET_KEY + self.recipient_user_id)
        self.enc_message = key.encrypt(message.encode())
        self.date_last_update = datetime.utcnow()

    # def decrypted(self):
    #     key = Fernet(self.sender_user_id + SECRET_KEY + self.recipient_user_id)
    #     decMessage = key.decrypt(self.enc_message).decode()
