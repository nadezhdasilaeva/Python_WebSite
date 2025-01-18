from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlmodel import Session, select
from models import User, Avatar
from db import get_session
from jwt import decode
from config import SECRET_KEY, ALGORITHM
import base64


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/")
def input(request: Request):
    return templates.TemplateResponse("mainpage.html", {"request": request})


@router.get("/home")
def home(request: Request, db: Session=Depends(get_session)):
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
        course = db.query(Course).all()
        if image_db:
            image_decode = base64.b64encode(image_db.image).decode("utf-8")
            return templates.TemplateResponse("homepage.html", {"request": request, "img": image_decode, "course": course})
        else:
            return templates.TemplateResponse("homepage.html", {"request": request})
