
from unittest.mock import patch

from app.rag.vector_store import add_resume_chunk


def test_add_resume_chunk():
    with (
        patch(
            "app.rag.vector_store.generate_embedding",
            return_value=[0.1, 0.2, 0.3],
        ) as mock_embedding,
        patch(
            "app.rag.vector_store.collection.add"
        ) as mock_add,
    ):
        add_resume_chunk(
            chunk_id="test_project_001",
            text="Built an AI Interview Trainer using FastAPI and Gemini.",
            chunk_type="project",
            resume_id="test_resume_001",
        )

        mock_embedding.assert_called_once_with(
            "Built an AI Interview Trainer using FastAPI and Gemini."
        )

        mock_add.assert_called_once_with(
            ids=["test_project_001"],
            documents=[
                "Built an AI Interview Trainer using FastAPI and Gemini."
            ],
            embeddings=[[0.1, 0.2, 0.3]],
            metadatas=[
                {
                    "resume_id": "test_resume_001",
                    "type": "project",
                }
            ],
        )

    print("PASS: Resume chunk stored with correct metadata and embedding.")


if __name__ == "__main__":
    test_add_resume_chunk()
    print("All vector-store tests passed!")
