from app.rag.embedding import generate_embedding
from app.rag.vector_store import collection


def retrieve_context(query: str, top_k: int = 5):

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return {
        "documents": results["documents"][0],
        "metadata": results["metadatas"][0],
    }
