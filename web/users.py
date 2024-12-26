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
        return templates.TemplateResponse("account.html", {"request": request, "user": user})


@router.get("/avatar")
def create_avatar(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        response = RedirectResponse(url="/", status_code=302)
        return response
    else:
        return templates.TemplateResponse("UploadAvatar.html", {"request": request})


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

        # Check file size
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
