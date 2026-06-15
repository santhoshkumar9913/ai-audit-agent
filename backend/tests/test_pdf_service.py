import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_extract_pdf_text(tmp_path):
    """Test PDF text extraction with a mocked PdfReader."""
    from app.services.pdf_service import extract_pdf_text

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample audit text here"

    with patch("app.services.pdf_service.PdfReader") as MockReader:
        instance = MockReader.return_value
        instance.pages = [mock_page]
        text = extract_pdf_text(str(tmp_path / "dummy.pdf"))

    assert "Sample audit text here" in text
    assert "[Page 1]" in text


def test_search_pdf_found(tmp_path):
    from app.services.pdf_service import search_pdf

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "The procurement process had a control weakness."

    with patch("app.services.pdf_service.PdfReader") as MockReader:
        instance = MockReader.return_value
        instance.pages = [mock_page]
        results = search_pdf(str(tmp_path / "dummy.pdf"), "procurement")

    assert len(results) == 1
    assert results[0]["page"] == 1
    assert "procurement" in results[0]["snippet"].lower()


def test_search_pdf_not_found(tmp_path):
    from app.services.pdf_service import search_pdf

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Nothing relevant here."

    with patch("app.services.pdf_service.PdfReader") as MockReader:
        instance = MockReader.return_value
        instance.pages = [mock_page]
        results = search_pdf(str(tmp_path / "dummy.pdf"), "ZZZNOMATCH")

    assert results == []
