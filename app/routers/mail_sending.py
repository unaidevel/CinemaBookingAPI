from typing import List

# from fastapi import APIRouter
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.zoho.eu",  
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)


# email_router = APIRouter()


# @email_router.post('/email')
async def simple_send(email_to:EmailSchema):
    message = MessageSchema(
        subject='Booking confirmation',
        recipients=email_to.email,
        body='Thank you for your booking. Enjoy the film!',
        subtype='plain'
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": 'email has been sent'})
