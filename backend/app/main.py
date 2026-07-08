from fastapi import FastAPI

app = FastAPI(
    title="Interview Trainer Agent",
    version="1.0.0",
    description="AI-powered Interview Trainer using RAG"
)


@app.get("/")
def home():
    return {
        "message": "Interview Trainer API is running 🚀"
    }
