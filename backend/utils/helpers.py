def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text
def format_history(chat_history):
    return "\n".join(f"{entry['role']}: {entry['content']}" for entry in chat_history)