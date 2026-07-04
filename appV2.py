
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

from dotenv import load_dotenv
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



# print(vector_store.index_to_docstore_id)



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
