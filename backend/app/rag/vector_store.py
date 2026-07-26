from app.rag.embedding import generate_embedding
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="resume_collection"
)


def add_resume_chunk(chunk_id: str, text: str):
    embedding = generate_embedding(text)

    collection.add(
        ids=[chunk_id],
        documents=[text],
        embeddings=[embedding]
    )