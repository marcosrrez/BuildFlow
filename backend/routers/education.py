from fastapi import APIRouter, HTTPException, Query
from backend.services.knowledge_base import KnowledgeService
from backend.schemas.education import KnowledgeEntryRead

router = APIRouter()

@router.get("/education/term/{term_id}", response_model=KnowledgeEntryRead)
def get_term(term_id: str):
    entry = KnowledgeService.get_entry(term_id)
    if not entry:
        raise HTTPException(404, "Educational content not found")
    return entry

@router.get("/education/search", response_model=list[KnowledgeEntryRead])
def search_education(q: str = Query(..., min_length=2)):
    return KnowledgeService.search(q)
