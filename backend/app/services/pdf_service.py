from pypdf import PdfReader
from pathlib import Path


def extract_pdf_text(file_path: str) -> str:
    """Extract all text from a PDF file."""
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(f"[Page {i + 1}]\n{text}")
    return "\n\n".join(pages)


def search_pdf(file_path: str, query: str) -> list[dict]:
    """Search PDF pages for a keyword, return matching page snippets."""
    reader = PdfReader(file_path)
    results = []
    q = query.lower()
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if q in text.lower():
            # Return surrounding context
            idx = text.lower().find(q)
            start = max(0, idx - 200)
            end = min(len(text), idx + 200)
            results.append({"page": i + 1, "snippet": text[start:end]})
    return results
