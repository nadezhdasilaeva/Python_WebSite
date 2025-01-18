from fastapi import APIRouter, Request, Depends, responses, status, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
from models import User, Avatar, Course,  Test
from utils import hash_password, get_xlsx, verify_access_token
from db import get_session
from sqlmodel import Session, select
from jwt import decode
from config import SECRET_KEY, ALGORITHM

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/article/{id}")
def theory(request: Request, id:int , db:Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        course = db.query(Course).filter(Course.id == id).first()
        course_data = course.data
        return templates.TemplateResponse("article1.html", {"request": request, "course_data": course_data})


@router.get("/tests/{test_id}")
def test(request: Request, test_id: int, db:Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    messages = {}
    errors = {}
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        course = db.query(Course).filter(Course.id == test_id).first()
        tests = db.exec(select(Test).where(Test.courses_id == test_id)).all()
        return templates.TemplateResponse("test.html", {"request": request, "tests": tests, "course": course, "messages": messages, "errors": errors})


@router.post("/tests/{test_id}/{id}")
async def answer_test(request: Request, test_id: int, id: int, db: Session = Depends(get_session)):
    form = await request.form()
    answer = form.get("answer")
    test = db.exec(select(Test).where(Test.id == id)).first()
    if not test:
        response = RedirectResponse(url="/home", status_code=302)
        return response
    messages = {}
    errors = {}
    if test.data[0]["true_answer"] == answer:
        messages[id] = "Верно!"
    else:
        errors[id] = "Неверно!"
    course = db.query(Course).filter(Course.id == test_id).first()
    tests = db.exec(select(Test).where(Test.courses_id == test_id)).all()
    print(messages)
    print(errors)
    return templates.TemplateResponse("test.html", {"request": request, "messages": messages, "tests": tests, "errors": errors, "course": course})