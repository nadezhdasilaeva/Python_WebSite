from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from sqlmodel import SQLModel
from starlette.responses import FileResponse

from db import engine
from routers import user, course, test, video, admin, message


from web import login as web_login
from web import input as web_input
from web import users as web_users
from web import theory as web_theorys
# from web import test as web_tests


if __name__ == '__main__':
    SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(course.router)
app.include_router(test.router)
app.include_router(video.router)
app.include_router(admin.router)
app.include_router(message.router)

app.include_router(web_login.router)
app.include_router(web_input.router)
app.include_router(web_users.router)
app.include_router(web_theorys.router)


if __name__ == '__main__':
    uvicorn.run(app, port=8001)
