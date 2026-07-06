from fastapi import FastAPI
from app.config import APP_NAME, APP_VERSION
from app.database.mongodb import test_connection
from app.api.auth import router as auth_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)


@app.on_event("startup")
def startup():
    test_connection()


app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "status": "Backend is running successfully!"
    }
