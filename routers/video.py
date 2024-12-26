import os

import aiofiles
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from starlette.responses import HTMLResponse, StreamingResponse

from db import get_session
from models import Video, User
from schemas import GetVideoByName, GetVideoByCourse, ReturnVideoSearch
from utils import verify_access_token

router = APIRouter(tags=['video'],
                   responses={404: {"description": "Not found"}})


@router.post('/get_video_tutorials/title_topic/')
def get_video_tutorials_title_topic(data: GetVideoByName, session: Session = Depends(get_session)):
    query = select(Video)

    if not data.title:
        query = query.where(Video.title == data.title)
    if not data.topic:
        query = query.where(Video.topic == data.topic)

    offset = data.offset
    limit = data.limit
    query = query.offset(offset).limit(limit)

    videos = session.exec(query).all()
    return [ReturnVideoSearch(
        course_id=video.course_id,
        title=video.title,
        topic=video.topic,
        date_create=video.date_create,
        date_last_update=video.date_last_update
    ) for video in videos]


@router.post('/get_video_tutorials/course_id/')
def get_video_tutorials_course_id(data: GetVideoByCourse, session: Session = Depends(get_session)):
    query = select(Video).where(Video.course_id == data.course_id)

    offset = data.offset
    limit = data.limit
    query = query.offset(offset).limit(limit)

    videos = session.exec(query).all()
    return [ReturnVideoSearch(
        course_id=video.course_id,
        title=video.title,
        topic=video.topic,
        date_create=video.date_create,
        date_last_update=video.date_last_update
    ) for video in videos]


@router.get('/get_video_tutorial/{video_id}/', response_class=StreamingResponse)
async def get_video_tutorial_id(video_id: int, user: User = Depends(verify_access_token),
                                session: Session = Depends(get_session)):
    if user.role == 'BAN':
        raise HTTPException(status_code=403)

    video = session.exec(select(Video).where(Video.id == video_id)).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    path = video.file_path  # Путь к видео

    # Проверяем, существует ли файл
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    # Асинхронный генератор для потоковой передачи файла
    async def iterfile():
        async with aiofiles.open(path, mode='rb') as file_like:
            while True:
                chunk = await file_like.read(1024)  # Читаем 1024 байта за раз
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(iterfile(), media_type="video/mp4")  # Замените media_type на нужный тип, если необходимо