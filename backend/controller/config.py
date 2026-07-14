import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')

class Config:

    SECRET_KEY=os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL")
    SECURITY_PASSWORD_HASH =os.getenv("SECURITY_PASSWORD_HASH")
    SECURITY_PASSWORD_SALT=os.getenv("SECURITY_PASSWORD_SALT")
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECURITY_TOKEN_AUTHENTICATION_HEADER='Authorization'
    UPLOAD_FOLDER=UPLOAD_FOLDER