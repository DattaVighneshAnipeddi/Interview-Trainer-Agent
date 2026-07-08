from fastapi import FastAPI
from app.routers import upload
from app.routers import gemini

app = FastAPI(
    title="Interview Trainer Agent",
    version="1.0.0",
    description="AI-powered Interview Trainer using RAG"
)

app.include_router(upload.router)
app.include_router(gemini.router)


@app.get("/")
def home():
    return {
        "message": "Interview Trainer API is running 🚀"
    }
