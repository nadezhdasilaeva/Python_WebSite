from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import Course, User, CompletedCourses, FavouritesCourse
from schemas import GetCourse, CourseResponse
from utils import verify_access_token

router = APIRouter(tags=['course'],
                   responses={404: {"description": "Not found"}})


@router.post('/get_courses/', response_model=List[CourseResponse])
def get_courses(data: GetCourse, session: Session = Depends(get_session)):
    query = select(Course)

    if data.title != 'None':
        query = query.where(Course.title == data.title)
    if data.topic != 'None':
        query = query.where(Course.topic == data.topic)

    offset = data.offset
    limit = data.limit
    query = query.offset(offset).limit(limit)

    courses = session.exec(query).all()
    return courses


@router.get('/get_course/{course_id}')
def get_course_data(course_id: int, user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role == 'BAN':
        raise HTTPException(status_code=403)
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(status_code=404)
    return course


@router.put('/get_course/{course_id}/complete')
def complete_course(course_id: int, user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role == 'BAN':
        raise HTTPException(status_code=403)
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(status_code=404)

    complete_co = CompletedCourses(
        user_id=user.id,
        course_id=course_id,
        title=course.title,
        topic=course.topic
    )
    session.add(complete_co)
    session.commit()
    raise HTTPException(status_code=200)


@router.put('/get_course/{course_id}/favourites')
def favourites_course(course_id: int, user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role == 'BAN':
        raise HTTPException(status_code=403)
    course = session.exec(select(Course).where(Course.id == course_id)).first()
    if not course:
        raise HTTPException(status_code=404)

    complete_fa = FavouritesCourse(
        user_id=user.id,
        course_id=course_id,
        title=course.title,
        topic=course.topic
    )
    session.add(complete_fa)
    session.commit()
    raise HTTPException(status_code=200)