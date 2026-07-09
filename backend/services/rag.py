from backend.services.vector_store import get_retriever
from backend.services.llm import get_llm
from backend.prompts.prompt import get_prompt
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from backend.utils.helpers import format_docs, format_history
from backend.services.history import get_or_create_session, get_recent_history


def rag_answer(query, url, session_id):
    retriever = get_retriever(url)
    llm = get_llm()
    chat_history = get_recent_history(session_id)
    prompt = get_prompt()

    

    parser = StrOutputParser()

    parallel_chain = RunnableParallel(
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
            "chat_history": RunnableLambda(lambda _: format_history(chat_history))
        }
    )

    main_chain = parallel_chain | prompt | llm | parser
    ans = main_chain.invoke(query)

    
    return ans