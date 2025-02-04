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


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/account")
def account(request: Request, db: Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("account.html", {"request": request, "user": user, "img": image_decode})
        else:
            return templates.TemplateResponse("account.html", {"request": request, "user": user})


@router.get("/avatar")
def create_avatar(request: Request, db:Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    if token:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("UploadAvatar.html", {"request": request, "img": image_decode})
        else:
            return templates.TemplateResponse("UploadAvatar.html", {"request": request})
    else:
        response = RedirectResponse(url="/", status_code=302)
        return response


@router.post("/upload_avatar")
async def create_avatar(request: Request, file: UploadFile = File(...), db: Session = Depends(get_session)):
    errors = []
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        image_data = await file.read()
        if len(image_data) > 2 * 1024 * 1024:
            errors.append("Файл слишком большой. Максимальный допустимый размер 2 МВ.")
            return templates.TemplateResponse("UploadAvatar.html", {"request": request, "errors": errors})
        if not image_db:
            image_instance = Avatar(user_id=user.id, image=image_data)
            db.add(image_instance)
            db.commit()
            response = RedirectResponse(url="/account", status_code=302)
            return response
        else:
            image_db.update_avatar(image_data)
            db.add(image_db)
            db.commit()
            db.refresh(image_db)
            response = RedirectResponse(url="/account", status_code=302)
            return response


@router.get("/edit_account")
def edit_account(request: Request, db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("edit_account.html", {"request": request, "user": user, "img": image_decode})
        else:
            return templates.TemplateResponse("edit_account.html", {"request": request, "user": user})

@router.post("/edit_account")
async def update_account(request: Request, db: Session = Depends(get_session)):
    form_data = await request.form()
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        scheme, _, param = token.partition(" ")
        payload = decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        user = db.query(User).filter(User.id == id).first()
        image_db = db.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            new_name = form_data.get("name")
            new_email = form_data.get("email")
            new_phone = form_data.get("phone")


            duplicate_email = db.exec(select(User).where(User.email == new_email).where(User.id != id)).first()
            if duplicate_email:
                errors = ["Email уже занят другим пользователем."]
                return templates.TemplateResponse("edit_account.html", {"request": request, "user": user, "errors": errors, "img": image_decode})


            duplicate_phone = db.exec(select(User).where(User.phone == new_phone).where(User.id != id)).first()
            if duplicate_phone:
                errors = ["Телефон уже занят другим пользователем."]
                return templates.TemplateResponse("edit_account.html", {"request": request, "user": user, "errors": errors,"img": image_decode})


            user.name = new_name
            user.email = new_email
            user.phone = new_phone
            db.commit()

            return RedirectResponse(url="/account", status_code=302)
        else:
            new_name = form_data.get("name")
            new_email = form_data.get("email")
            new_phone = form_data.get("phone")


            duplicate_email = db.exec(select(User).where(User.email == new_email).where(User.id != id)).first()
            if duplicate_email:
                errors = ["Email уже занят другим пользователем."]
                return templates.TemplateResponse("edit_account.html", {"request": request, "user": user, "errors": errors})


            duplicate_phone = db.exec(select(User).where(User.phone == new_phone).where(User.id != id)).first()
            if duplicate_phone:
                errors = ["Телефон уже занят другим пользователем."]
                return templates.TemplateResponse("edit_account.html", {"request": request, "user": user, "errors": errors})


            user.name = new_name
            user.email = new_email
            user.phone = new_phone
            db.commit()

            return RedirectResponse(url="/account", status_code=302)
