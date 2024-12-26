from fastapi import APIRouter, Request, Depends, responses, status, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
from models import User, Avatar
from utils import hash_password, get_xlsx, verify_access_token
from db import get_session
from sqlmodel import Session, select
from jwt import decode
from config import SECRET_KEY, ALGORITHM
# import base64


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/all_users")
def all_users(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        users = db.query(User).all()
        return templates.TemplateResponse("all_users.html", {"request": request, "users": users})
    else:
        errors.append("Не вошли в аккаунт/Не являетесь администратором")
        return templates.TemplateResponse("homepage.html", {"request": request, "errors": errors})


@router.post("/all_users/{id}")
def all_users(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        errors.append("Войдите в аккаунт")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors})
    if role != "super_user":
        errors.append("Вы не являетесь администратором")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors})
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("all_users.html", {"request": request, "errors": errors})
    db.delete(user)
    db.commit()
    users = db.query(User).all()
    return templates.TemplateResponse("all_users.html", {"request": request, "users": users})
