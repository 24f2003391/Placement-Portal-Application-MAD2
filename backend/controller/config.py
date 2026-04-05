import os
from dotenv import load_dotenv

load_dotenv()

class config:

    SECRET_KEY=os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL")
    SECURITY_PASSWORD_HASH =os.getenv("SECURITY_PASSWORD_HASH")
    SECURITY_PASSWORD_SALT=os.getenv("SECURITY_PASSWORD_SALT")
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECURITY_TOKEN_AUTHENTICATION_HEADER='Authorization'