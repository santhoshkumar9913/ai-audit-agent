import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Patch database so tests don't need a real MongoDB."""
    mock_collection = MagicMock()
    mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="507f1f77bcf86cd799439011"))
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_collection.find = MagicMock(return_value=_async_iter([]))
    mock_collection.delete_one = AsyncMock()

    mock_db_obj = MagicMock()
    mock_db_obj.documents = mock_collection
    mock_db_obj.sessions = mock_collection

    with patch("app.core.database.connect_db", new=AsyncMock()), \
         patch("app.core.database.close_db", new=AsyncMock()), \
         patch("app.core.database.get_db", return_value=mock_db_obj):
        yield mock_db_obj


class _async_iter:
    def __init__(self, items):
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration:
            raise StopAsyncIteration


@pytest.mark.asyncio
async def test_health():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_documents_empty(mock_db):
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/documents/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_sessions_empty(mock_db):
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/chat/sessions")
    assert resp.status_code == 200
    assert resp.json() == []
