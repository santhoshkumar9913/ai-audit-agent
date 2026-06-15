from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentMeta(BaseModel):
    id: Optional[str] = None
    filename: str
    file_type: str  # "excel" | "pdf"
    upload_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    sheet_names: Optional[list[str]] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseModel):
    id: Optional[str] = None
    session_id: str
    document_ids: list[str] = []
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
