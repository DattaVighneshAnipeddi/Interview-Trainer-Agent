from fastapi import FastAPI
from app.config import APP_NAME, APP_VERSION

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

@app.get("/")
def home():
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "status": "Backend is running successfully!"
}