from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer, status = generate_response(request.query)
    return {
        "answer": answer,
        "status": status
    }