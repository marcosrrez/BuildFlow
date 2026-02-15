import os
import uuid
from pathlib import Path
from backend.config import settings


def save_upload(file_bytes: bytes, filename: str, subfolder: str = "documents") -> str:
    upload_dir = Path(settings.upload_dir) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = upload_dir / unique_name
    dest.write_bytes(file_bytes)
    return str(dest)


def get_upload_path(subfolder: str) -> Path:
    p = Path(settings.upload_dir) / subfolder
    p.mkdir(parents=True, exist_ok=True)
    return p
