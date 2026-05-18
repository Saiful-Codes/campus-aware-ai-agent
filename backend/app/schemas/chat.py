from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., max_length=2000)
    debug: bool = False


class ChatResponse(BaseModel):
    answer: str
    status: str
    debug: Optional[Dict[str, Any]] = None
