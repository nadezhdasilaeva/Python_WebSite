import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from starlette.responses import FileResponse

from config import PASS_ADMIN, EMAIL_ADMIN, VIDEO_UPLOAD_PATH
from db import get_session
from models import User, Course, Test, Video
from schemas import AddUpdateCourse, AddUpdateTest, AddCourse, AddTest, AddVideo, UpdateVideo, GetUserForAdmin
from utils import hash_password, verify_access_token, get_xlsx

router = APIRouter(prefix='/admin', tags=['admin'],
                   responses={404: {"description": "Not found"}})


@router.post('/create_first_admin/')
def create_admin(session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.role == 'super_user')).first():
        raise HTTPException(status_code=400)
    hash_pass = hash_password(PASS_ADMIN)
    user = User(email=EMAIL_ADMIN,
                hash_password=hash_pass,
                name='admin',
                phone='+78005553535',
                )
    user.super_user()
    session.add(user)
    session.commit()
    raise HTTPException(status_code=201)


@router.get('/get_all_user/', response_model=List[GetUserForAdmin])
def get_all_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    users = session.exec(select(User)).all()
    return users


@router.get('/get_user/xlsx')
def get_verify_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    name = 'users'
    users = session.exec(select(User)).all()
    get_xlsx(users, f'{name}.xlsx')
    return FileResponse(path=f'{name}.xlsx', filename=f'{name}.xlsx', media_type='multipart/form-data')


@router.put('/BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'BAN':
        raise HTTPException(status_code=400, detail='The user has already been blocked')
    user.ban_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/un_BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role != 'BAN':
        raise HTTPException(status_code=400, detail='The user is not blocked')
    user.user_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.delete('/del_user/{user_id}')
def del_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    session.delete(user)
    session.commit()
    raise HTTPException(status_code=204)


@router.put('/make_super_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'BAN':
        raise HTTPException(status_code=400, detail='The user has already been blocked')
    if user.role == 'super_user':
        raise HTTPException(status_code=400, detail='The user is already a super user')
    user.super_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/un_make_super_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role != 'super_user':
        raise HTTPException(status_code=400, detail='The user is not a super user')
    user.user_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.post('/add_course/')
def add_course(data: AddCourse, su_user: User = Depends(verify_access_token),
               session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    course = Course(
        title=data.title,
        topic=data.topic,
        data=data.data
    )
    session.add(course)
    session.commit()
    raise HTTPException(status_code=200)


@router.put('/update_course/{course_id}')
def update_course(course_id: int, data: AddUpdateTest, su_user: User = Depends(verify_access_token),
                  session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    course.update_data(data.data)
    session.add(course)
    session.commit()
    session.refresh(course)
    raise HTTPException(status_code=200)


@router.delete('/del_course/{course_id}')
def del_course(course_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(status_code=404, detail='Course not found')
    session.delete(course)
    session.commit()
    raise HTTPException(status_code=204)


@router.post('/add_test/{courses_id}')
def add_test(courses_id: int, data: AddTest, su_user: User = Depends(verify_access_token),
             session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)

    # Преобразуем список TestData в список словарей
    test_data = [test_data.dict() for test_data in data.data]

    test = Test(
        courses_id=courses_id,
        title=data.title,
        topic=data.topic,
        data=test_data
    )
    session.add(test)
    session.commit()
    raise HTTPException(status_code=200)


@router.put('/update_tset/{test_id}')
def update_tset(test_id: int, data: AddUpdateTest, su_user: User = Depends(verify_access_token),
                session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    test = session.exec(select(Test).where(Test.id == test_id)).first()
    test.update_data(data.data)
    session.add(test)
    session.commit()
    session.refresh(test)
    raise HTTPException(status_code=200)


@router.delete('/del_test/{test_id}')
def del_test(test_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    test = session.exec(select(Test).where(Test.id == test_id)).first()
    if not test:
        raise HTTPException(status_code=404, detail='Test not found')
    session.delete(test)
    session.commit()
    raise HTTPException(status_code=204)


@router.post('/add_video')
async def add_video(
        course_id: int = Form(...),
        title: Optional[str] = Form(default='Video tutorial', max_length=255),
        topic: Optional[str] = Form(default='topic', max_length=255),
        file: UploadFile = File(...),
        su_user: User = Depends(verify_access_token),
        session: Session = Depends(get_session)
):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)

    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(status_code=404)

    # Проверка и создание директории, если она не существует
    if not os.path.exists(VIDEO_UPLOAD_PATH):
        os.makedirs(VIDEO_UPLOAD_PATH)

    # Сохранение файла на сервере
    unique_filename = f"{uuid.uuid4()}_{file.filename}"  # Добавление UUID к имени файла
    file_path = os.path.join(VIDEO_UPLOAD_PATH, unique_filename)  # Полный путь к файлу
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Получение типа контента
    content_type = file.content_type

    # Создание записи в базе данных
    video = Video(
        course_id=course_id,
        title=title,
        topic=topic,
        file_path=file_path,
        content_type=content_type,
        date_create=datetime.utcnow(),
        date_last_update=datetime.utcnow()
    )
    session.add(video)
    session.commit()
    raise HTTPException(status_code=201)


@router.put('/update_video_title/{video_id}')
async def update_video_title(
        video_id: int,
        data: UpdateVideo,
        su_user: User = Depends(verify_access_token),
        session: Session = Depends(get_session)  # Предполагается, что вы используете зависимость для получения сессии
):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    # Найти видео по ID
    video = session.exec(select(Video).where(Video.id == video_id)).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Обновить название видео и дату последнего обновления
    video.update_title(data.title)

    # Сохранить изменения в базе данных
    session.commit()
    session.refresh(video)
    raise HTTPException(status_code=200)


@router.delete('/delete_video/{video_id}')
def del_video(
        video_id: int,
        su_user: User = Depends(verify_access_token),
        session: Session = Depends(get_session)
):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    video = session.exec(select(Video).where(Video.id == video_id)).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Удалить файл с сервера
    if os.path.exists(video.file_path):
        os.remove(video.file_path)

    # Удалить запись из базы данных
    session.delete(video)
    session.commit()
    raise HTTPException(status_code=200)
