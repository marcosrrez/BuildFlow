from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from backend.database import get_db
from backend.models.document import DocumentCategory, Document
from backend.schemas.document import (
    DocumentCategoryCreate, DocumentCategoryRead,
    DocumentRead,
)
from backend.utils.file_storage import save_upload

router = APIRouter()


@router.get("/projects/{project_id}/documents/categories", response_model=list[DocumentCategoryRead])
def list_categories(project_id: int, db: Session = Depends(get_db)):
    return db.query(DocumentCategory).filter(DocumentCategory.project_id == project_id).order_by(DocumentCategory.sort_order).all()


@router.post("/projects/{project_id}/documents/categories", response_model=DocumentCategoryRead, status_code=201)
def create_category(project_id: int, data: DocumentCategoryCreate, db: Session = Depends(get_db)):
    cat = DocumentCategory(project_id=project_id, **data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/projects/{project_id}/documents", response_model=list[DocumentRead])
def list_documents(project_id: int, category_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Document).filter(Document.project_id == project_id)
    if category_id is not None:
        q = q.filter(Document.category_id == category_id)
    return q.order_by(Document.created_at.desc()).all()


@router.post("/projects/{project_id}/documents", response_model=DocumentRead, status_code=201)
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    name: str = Form(""),
    category_id: int | None = Form(None),
    description: str = Form(""),
    tags: str = Form(""),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    path = save_upload(contents, file.filename or "file", "documents")
    doc_name = name or file.filename or "Untitled"
    ext = Path(file.filename or "").suffix.lstrip(".") if file.filename else None
    doc = Document(
        project_id=project_id, name=doc_name, file_path=path,
        file_type=ext, file_size=len(contents),
        category_id=category_id, description=description, tags=tags,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/projects/{project_id}/documents/{doc_id}", response_model=DocumentRead)
def get_document(project_id: int, doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.project_id == project_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/projects/{project_id}/documents/{doc_id}/download")
def download_document(project_id: int, doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.project_id == project_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    p = Path(doc.file_path)
    if not p.exists():
        raise HTTPException(404, "File not found on disk")
    return FileResponse(str(p), filename=doc.name)


@router.delete("/projects/{project_id}/documents/{doc_id}", status_code=204)
def delete_document(project_id: int, doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.project_id == project_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
