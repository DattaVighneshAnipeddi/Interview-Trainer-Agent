
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file and ensure the document is closed."""
    text_parts = []

    with fitz.open(file_path) as pdf:
        for page in pdf:
            text_parts.append(page.get_text())

    return "\n".join(text_parts)
