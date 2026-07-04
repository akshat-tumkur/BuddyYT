from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from backend.services.transcript_service import get_transcript
from backend.services.embeddings import get_embeddings

def build_vec_store(url):
    embeddings = get_embeddings()
    transcript = get_transcript(url)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])

    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    
    return retriever 
