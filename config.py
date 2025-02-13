import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345@localhost:3307/login"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
   