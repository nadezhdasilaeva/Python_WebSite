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
import base64
from typing import Optional


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/all_users")
def all_users(request: Request, db: Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        users = db.query(User).all()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("all_users.html", {"request": request, "img": image_decode, "users": users})
        else:
            return templates.TemplateResponse("all_users.html", {"request": request, "users": users})
    if token and (not role == "super_user"):
        response = RedirectResponse(url="/home", status_code=302)
        return response
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response    


@router.post("/all_users/{id}")
def all_users(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        response = RedirectResponse(url="/", status_code=302)
        return response
    db.delete(user)
    db.commit()
    users = db.query(User).all()
    return templates.TemplateResponse("all_users.html", {"request": request, "users": users})


@router.get("/BAN_user")
def BAN_user(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        users = db.query(User).all()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("BAN_users.html", {"request": request, "img": image_decode, "users": users})
        else:
            return templates.TemplateResponse("BAN_users.html", {"request": request, "users": users})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response  


@router.post("/BAN_user/{id}")
def BAN_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("BAN_users.html", {"request": request, "errors": errors})
    user.ban_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    users = db.query(User).all()
    response = RedirectResponse(url="/BAN_user", status_code=302)
    return response 
    # return templates.TemplateResponse("BAN_users.html", {"request": request, "users": users})


@router.post("/un_BAN_user/{id}")
def un_BAN_user(request: Request, id: int, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден")
        return templates.TemplateResponse("BAN_users.html", {"request": request, "errors": errors})
    user.user_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    users = db.query(User).all()
    response = RedirectResponse(url="/BAN_user", status_code=302)
    return response


@router.get("/status")
def status_users(request: Request, db: Session=Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        users = db.query(User).all()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("status.html", {"request": request, "img": image_decode, "users": users})
        else:
            return templates.TemplateResponse("status.html", {"request": request, "users": users})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response


@router.post("/user/{id}")
def user_role(request: Request, id: int, db: Session = Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден!")
        return templates.TemplateResponse("status.html", {"request": request, "errors": errors})
    user.user_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    response = RedirectResponse(url="/status", status_code=302)
    return response


@router.post("/teacher/{id}")
def teacher_role(request: Request, id: int, db: Session = Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден!")
        return templates.TemplateResponse("status.html", {"request": request, "errors": errors})
    user.teacher_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    response = RedirectResponse(url="/status", status_code=302)
    return response


@router.post("/admin/{id}")
def admin_role(request: Request, id: int, db: Session = Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    if role != "super_user":
        response = RedirectResponse(url="/", status_code=302)
        return response
    user = db.exec(select(User).where(User.id == id)).first()
    if not user:
        errors.append("Пользователь не найден!")
        return templates.TemplateResponse("status.html", {"request": request, "errors": errors})
    user.super_user()
    db.add(user)
    db.commit()
    db.refresh(user)
    response = RedirectResponse(url="/status", status_code=302)
    return response


@router.get("/update_password")
def update(request: Request, db: Session = Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("update_password.html", {"request": request, "img": image_decode})
        else:
            return templates.TemplateResponse("update_password.html", {"request": request})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response


@router.post("/update_password")
async def update(request: Request, db: Session = Depends(get_session)):
    errors = []
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    complete_password = form.get("complete_password")
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        admin = db.query(User).filter(User.id == id).first()
        user = db.query(User).filter(User.email == email).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == admin.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            if user is None:
                errors.append("Пользователь не найден!")
                return templates.TemplateResponse("update_password.html", {"request": request, "errors": errors})
            if user.role == 'BAN':
                errors.append("Пользователь заблокирован")
                return templates.TemplateResponse("update_password.html", {"request": request, "errors": errors})
            if password != complete_password:
                errors.append("Неверное повторение пароля")
                return templates.TemplateResponse("update_password.html", {"request": request, "errors": errors})
            user.hash_password = hash_password(password)
            db.add(user)
            db.commit()
            db.refresh(user)
            msg = "Пароль изменен"
            return templates.TemplateResponse("update_password.html", {"request": request, "msg": msg, "img": image_decode})
        else:
            if user is None:
                errors.append("Пользователь не найден!")
                return templates.TemplateResponse("update_password.html", {"request": request, "errors": errors})
            if user.role == 'BAN':
                errors.append("Пользователь заблокирован")
                return templates.TemplateResponse("update_password.html", {"request": request, "errors": errors})
            if password != complete_password:
                errors.append("Неверное повторение пароля")
                return templates.TemplateResponse("update_password.html", {"request": request, "errors": errors})
            user.hash_password = hash_password(password)
            db.add(user)
            db.commit()
            db.refresh(user)
            msg = "Пароль изменен"
            return templates.TemplateResponse("update_password.html", {"request": request, "msg": msg})


@router.get("/search_all_users")
def search_users(request: Request, query: Optional[str], db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    users = db.query(User).filter(User.email.contains(query)).all()
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("all_users.html", {"request": request, "img": image_decode, "users": users})
        else:
            return templates.TemplateResponse("all_users.html", {"request": request, "users": users})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response
    

@router.get("/search_status")
def search_users(request: Request, query: Optional[str], db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    users = db.query(User).filter(User.email.contains(query)).all()
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("status.html", {"request": request, "img": image_decode, "users": users})
        else:
            return templates.TemplateResponse("status.html", {"request": request, "users": users})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response
    

@router.get("/search_BAN_users")
def search_users(request: Request, query: Optional[str], db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    role = request.cookies.get("role")
    users = db.query(User).filter(User.email.contains(query)).all()
    if token and (role == "super_user"):
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("BAN_users.html", {"request": request, "img": image_decode, "users": users})
        else:
            return templates.TemplateResponse("BAN_users.html", {"request": request, "users": users})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response
