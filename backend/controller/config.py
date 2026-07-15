import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')
EXPORT_FOLDER = os.path.join(BASE_DIR, "instance", "exports")

class Config:

    SECRET_KEY=os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL")
    SECURITY_PASSWORD_HASH =os.getenv("SECURITY_PASSWORD_HASH")
    SECURITY_PASSWORD_SALT=os.getenv("SECURITY_PASSWORD_SALT")
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECURITY_TOKEN_AUTHENTICATION_HEADER='Authorization'
    UPLOAD_FOLDER=UPLOAD_FOLDER
    EXPORT_FOLDER=EXPORT_FOLDER

    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = "placement.portal@iitm.local"