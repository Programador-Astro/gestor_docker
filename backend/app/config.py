from dotenv import load_dotenv
import os
from datetime import timedelta


load_dotenv()
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    CORS_HEADERS = 'Content-Type'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')

    MAIL_SERVER = os.getenv('ENVIO_EMAIL_SERVER')
    MAIL_PORT = os.getenv('ENVIO_EMAIL_PORTA')
    MAIL_USERNAME = os.getenv("ENVIO_EMAIL_EMAIL")
    MAIL_PASSWORD = os.getenv("ENVIO_EMAIL_SENHA")
    MAIL_USE_TLS = True



   
