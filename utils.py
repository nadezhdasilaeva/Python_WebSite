import smtplib
import urllib
from datetime import timedelta, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hashlib import sha256
from random import randint

import openpyxl
from cryptography.fernet import Fernet
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, encode, decode
from sqlmodel import select, Session

from config import SECRET_KEY, ALGORITHM, PASSWORD, USERNAME, HOST, PORT
from db import get_session
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_error = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}, )


def create_access_token(data: dict, exp: timedelta = None):
    to_encode = data.copy()
    if exp:
        expire = datetime.utcnow() + exp
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt


def verify_access_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_error
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise credentials_error
        return user
    except PyJWTError:
        raise credentials_error


def hash_password(password: str):
    return sha256(password.encode()).hexdigest()


def send_mail(reception_email: str, code: str):
    # create message object instance
    msg = MIMEMultipart()

    # set up the parameters of the message
    password = PASSWORD
    msg['From'] = USERNAME
    msg['To'] = reception_email
    msg['Subject'] = "Reset password"

    # add in the message body
    msg.attach(MIMEText(code, 'plain'))

    # create server
    server = smtplib.SMTP(f'{HOST}: {PORT}')
    server.starttls()
    server.login(msg['From'], password)
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


async def get_meme():
    urllib.request.urlretrieve('https://img.randme.me/', "meme.jpg")


def gen_res_key():
    num = str(randint(1, 999999))
    return ('0' * (6 - len(num))) + num


def get_xlsx(users, file_name):
    # Create a workbook and select the active sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    # Write the headers
    headers = ['id', 'date_reg', 'email', 'role', 'name']
    sheet.append(headers)
    # Write the users
    for user in users:
        user = dict(user)
        row = [user[header] for header in headers]
        sheet.append(row)
    # Save the workbook
    workbook.save(file_name)


def decrypted(sender_user_id, recipient_user_id, enc_message):
    key = Fernet(sender_user_id + SECRET_KEY + recipient_user_id)
    decoded_message = key.decrypt(enc_message).decode()
    return decoded_message
