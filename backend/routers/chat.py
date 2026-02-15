from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.chat_service import chat

router = APIRouter()


@router.post("/projects/{project_id}/chat", response_model=ChatResponse)
async def project_chat(project_id: int, req: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = await chat(
            db, project_id, req.message,
            [{"role": m.role, "content": m.content} for m in req.history],
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(500, f"Chat error: {str(e)}")
