from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from backend.services.transcript_service import get_transcript
from backend.services.embeddings import get_embeddings
from pathlib import Path
import hashlib
import re

def build_vec_store(url):
    embeddings = get_embeddings()
    cache_dir = _get_video_cache_dir(url)
    index_file = cache_dir / "index.faiss"

    if index_file.exists():
        vector_store = FAISS.load_local(
            str(cache_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    transcript = get_transcript(url)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])

    vector_store = FAISS.from_documents(chunks, embeddings)
    cache_dir.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(cache_dir))
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})


def _get_video_cache_dir(url):
    video_id = _extract_video_id(url)
    cache_root = Path(__file__).resolve().parents[1] / "cache" / "faiss"
    return cache_root / video_id


def _extract_video_id(url):
    patterns = [
        r"[?&]v=([a-zA-Z0-9_-]+)",
        r"youtu\.be/([a-zA-Z0-9_-]+)",
        r"shorts/([a-zA-Z0-9_-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return hashlib.sha1(url.encode("utf-8")).hexdigest()
