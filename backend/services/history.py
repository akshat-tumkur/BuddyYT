import uuid
from typing import Dict, List, Optional

# In-memory session store: session_id -> {url, messages}
session_store: Dict[str, Dict[str, object]] = {}


def create_session(url: str) -> str:
    session_id = uuid.uuid4().hex
    session_store[session_id] = {
        "url": url,
        "messages": [],
    }
    return session_id


def get_or_create_session(session_id: Optional[str], url: str) -> str:
    if session_id and session_id in session_store:
        session_store[session_id]["url"] = url
        return session_id
    return create_session(url)


def add_message(session_id: str, role: str, content: str) -> None:
    session = session_store.setdefault(
        session_id,
        {"url": "", "messages": []},
    )
    session["messages"].append({"role": role, "content": content})


def get_recent_history(session_id: str, limit: int = 8) -> List[Dict[str, str]]:
    session = session_store.get(session_id)
    if not session:
        return []

    messages = session.get("messages", [])
    return list(messages[-limit:])
