from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from db import get_session


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")



@router.get("/")
def input(request: Request):
    return templates.TemplateResponse("mainpage.html", {"request": request})

# @router.get("/register")
# def register(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})


@router.get("/home")
def home(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})