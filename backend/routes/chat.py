from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.history import add_message, get_or_create_session
from backend.services.rag import rag_answer

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    url: str
    session_id: str | None = None


@router.post("/chat")
def chat(request: ChatRequest):
    session_id = get_or_create_session(request.session_id, request.url)
    ans = rag_answer(request.query, request.url, session_id)
    add_message(session_id, "user", request.query)
    add_message(session_id, "assistant", ans)

    return {
    "answer": ans,
    "session_id": session_id,
    }