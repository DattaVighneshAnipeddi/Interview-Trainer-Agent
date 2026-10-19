
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.rate_limiter import limiter

from app.database import init_db
from app.routers import auth, upload, gemini, interview


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

# Register SlowAPI.
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.include_router(upload.router)
app.include_router(gemini.router)
app.include_router(interview.router)
app.include_router(auth.router)


@app.get("/")
def home(request: Request):
    return {
        "message": "Interview Trainer API is running"
    }
