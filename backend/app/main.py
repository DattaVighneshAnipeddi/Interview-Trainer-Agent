
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import upload, gemini, interview


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database before serving requests.
    init_db()
    yield


app = FastAPI(
    title="Interview Trainer Agent",
    version="1.0.0",
    description="AI-powered Interview Trainer using RAG",
    lifespan=lifespan,
)

app.include_router(upload.router)
app.include_router(gemini.router)
app.include_router(interview.router)


@app.get("/")
def home():
    return {
        "message": "Interview Trainer API is running"
    }
