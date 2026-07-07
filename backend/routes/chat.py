from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.history import add_message, get_or_create_session, get_recent_history
from backend.services.rag import rag_answer

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    url: str
    session_id: str | None = None


@router.post("/chat")
def chat(request: ChatRequest):
    ans = rag_answer(request.query, request.url, request.session_id)
    add_message(request.session_id, "user", request.query)
    add_message(request.session_id, "assistant", ans)
    chat_history = get_recent_history(request.session_id)

    return {
    "answer": ans,
    "chat_history": chat_history
    }