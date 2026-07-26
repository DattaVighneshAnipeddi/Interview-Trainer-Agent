from app.rag.embedding import generate_embedding

embedding = generate_embedding("Python FastAPI Machine Learning")

print(len(embedding))
print(embedding[:10])  # Show the first 10 values