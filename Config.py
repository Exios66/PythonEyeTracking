import os

class Config:
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    HOST = "0.0.0.0"
    PORT = 5000
    CORS_ALLOWED_ORIGINS = "*"
