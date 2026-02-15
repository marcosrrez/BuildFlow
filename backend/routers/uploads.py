from fastapi import APIRouter, UploadFile, File
from backend.utils.file_storage import save_upload

router = APIRouter()


@router.post("/upload/photo")
async def upload_photo(file: UploadFile = File(...)):
    contents = await file.read()
    path = save_upload(contents, file.filename or "photo.jpg", "photos")
    return {"file_path": path}


@router.post("/upload/document")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()
    path = save_upload(contents, file.filename or "file", "documents")
    return {"file_path": path}
