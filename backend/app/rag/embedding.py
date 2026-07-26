from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    return model.encode(text).tolist()
from app.rag.embedding import generate_embedding

embedding = generate_embedding("Python FastAPI Machine Learning")

print(len(embedding))