import os
import shutil
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

from app.core.config import settings


def get_upload_path(filename: str) -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{filename}"
    return upload_dir / safe_name


async def save_upload(file: UploadFile) -> tuple[str, int]:
    """Save uploaded file to disk. Returns (path, size_bytes)."""
    dest = get_upload_path(file.filename)
    size = 0
    with open(dest, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)
            size += len(chunk)
    return str(dest), size


def delete_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
