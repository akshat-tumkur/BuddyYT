
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from youtube_transcript_api._errors import TranscriptsDisabled
import re
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
url = 'https://www.youtube.com/watch?v=utpELrpndc4'
video_id = re.search(r"v=([a-zA-Z0-9_-]+)", url).group(1)

try:
    fetched_transcript = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
    transcript_list = fetched_transcript.to_raw_data()
    transcript = " ".join(chunk["text"] for chunk in transcript_list)
    
    
except TranscriptsDisabled:
    print("No captions available for this video.")
except Exception as e:
    print(f"An error occurred: {e}")
    exit()


splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = FAISS.from_documents(chunks, embeddings)
# print(vector_store.index_to_docstore_id)

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.
      Chat history = {chat_history}  
      {context}

      Question: {question}

    """,
    input_variables = ['context', 'question', 'chat_history']
)



chat_history = []

def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text
def format_history(chat_history):
    return "\n".join(f"{entry['role']}: {entry['content']}" for entry in chat_history)

parser = StrOutputParser()

parallel_chain = RunnableParallel(
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough(),
        "chat_history": RunnableLambda(lambda _: format_history(chat_history))
    }
)

main_chain = parallel_chain | prompt | llm | parser

while True:
    question = input("Enter your question: ")
    if question.lower() == "exit":
        break
    chat_history.append({"role": "user", "content": question})
    ans = main_chain.invoke(question)
    chat_history.append({"role": "AI", "content": ans})
    print(ans)
