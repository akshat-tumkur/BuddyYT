from langchain_core.prompts import PromptTemplate

def get_prompt():
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
    return prompt