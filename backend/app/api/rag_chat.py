from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.rag_pipeline import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):
    try:
        answer = generate_answer(request.message)
        return {"response": answer}
    except Exception as exc:
        print("RAG ERROR:", exc)
        # response stays null so the mobile client falls through to /chat;
        # error: True is a structured signal for any future caller / log scan.
        return {"response": None, "error": True}
