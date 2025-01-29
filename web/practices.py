from fastapi import APIRouter, Request, Depends, responses, status, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
from models import User, Avatar, Course,  Test, Practice
from utils import hash_password, get_xlsx, verify_access_token
from db import get_session
from sqlmodel import Session, select
from jwt import decode
from config import SECRET_KEY, ALGORITHM
import base64
import subprocess


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/practices/{practice_id}/{id}")
def practice(request: Request, practice_id: int, id: int, db:Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    messages = {}
    errors = {}
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        course = db.query(Course).filter(Course.id == practice_id).first()
        practices = db.exec(select(Practice).where(Practice.courses_id == practice_id)).all()
        practice = db.exec(select(Practice).where(Practice.id == id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("practice.html", {
                "request": request, 
                "practices": practices,
                "practice": practice, 
                "course": course, 
                "messages": messages, 
                "errors": errors, 
                "img": image_decode
                })
        else:
            return templates.TemplateResponse("practice.html", {
                "request": request, 
                "practices": practices,
                "practice": practice,  
                "course": course, 
                "messages": messages, 
                "errors": errors
                })


@router.post("/practices/{practice_id}/{id}")
async def compile_code(request: Request, practice_id: int, id:int, db:Session=Depends(get_session)):
    form = await request.form()
    answer = form.get("answer")
    input_data = form.get("input_data")
    
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        course = db.query(Course).filter(Course.id == practice_id).first()
        practice = db.exec(select(Practice).where(Practice.id == id)).first()

        practices = db.exec(select(Practice).where(Practice.courses_id == practice_id)).all()
        
        if not practice:
            response = RedirectResponse(url="/home", status_code=302)
            return response
        messages = {}
        errors = {}
        if "input(" in answer and not input_data:
            errors[id] = "Неверно!"
            return templates.TemplateResponse("practice.html", {
                "request": request,
                "result": "Ошибка: Входные данные не предоставлены.",
                "practices": practices,
                "last_code": answer,
                "messages": messages,
                "errors": errors,
                "course": course,
                "practice": practice
            })

        try:
            with open("temp_code.py", "w", encoding='utf-8') as f:
                f.write(answer)

            result = subprocess.run(
                ["python", "temp_code.py"],
                input=input_data,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            if practice.data[0]["true_answer"].strip() == result.stdout.strip():
                messages[id] = "Верно!" 
            else:
                errors[id] = "Неверно!"

            if image_db:
                image_decode = base64.b64encode(image_db.image).decode("utf-8")
                return templates.TemplateResponse("practice.html", {
                    "request": request,
                    "result": result.stdout,
                    "practices": practices,
                    "last_code": answer,
                    "messages": messages,
                    "errors": errors,
                    "img": image_decode,
                    "course": course,
                    "practice": practice
                })
            else:
                return templates.TemplateResponse("practice.html", {
                    "request": request,
                    "result": result.stdout,
                    "practices": practices,
                    "last_code": answer,
                    "messages": messages,
                    "errors": errors,
                    "course": course,
                    "practice": practice,
                })
            
        except Exception as e:
            errors[id] = "Неверно!"
            return templates.TemplateResponse("practice.html", {
                "request": request,
                "result:": result.stdout,
                # "result": f"Ошибка: {str(e)}",
                "last_code": answer,
                "errors": errors,
                "img": image_decode,
                "practices": practices,
                "course": course,
                "practice": practice,
            })