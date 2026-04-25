from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import HTTPException
from app.rag.rag_pipeline import generate_answer

router = APIRouter()


# request format
class ChatRequest(BaseModel):
    message: str


# response endpoint
@router.post("/chat")
def chat(request: ChatRequest):
    try:
        answer = generate_answer(request.message)
        return {"response": answer}
    except Exception as e:
        print("RAG ERROR:", e)
        return {"response": None}  # IMPORTANT