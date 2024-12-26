import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get("MAIL_HOST")
USERNAME = os.environ.get("MAIL_USERNAME")
PASSWORD = os.environ.get("MAIL_PASSWORD")
PORT = os.environ.get("MAIL_PORT", 465)
# https://ethereal.email/create

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
VIDEO_UPLOAD_PATH = os.environ.get("VIDEO_UPLOAD_PATH")
LAB_UPLOAD_PATH = os.environ.get("LAB_UPLOAD_PATH")

PASS_ADMIN = os.environ.get("PASS_ADMIN")
EMAIL_ADMIN = os.environ.get("EMAIL_ADMIN")
