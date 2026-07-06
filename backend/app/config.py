import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")
DEBUG = os.getenv("DEBUG")

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")