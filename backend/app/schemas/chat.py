from typing import Any, Dict, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    debug: bool = False


class ChatResponse(BaseModel):
    answer: str
    status: str
    debug: Optional[Dict[str, Any]] = None