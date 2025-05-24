import chromadb
from chromadb.utils import embedding_functions
from langchain_chroma import Chroma
from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_gigachat.chat_models import GigaChat

def giga_query(query):
    # Инициализация ChromaDB
    chroma_client = chromadb.PersistentClient(path="/app/chroma_data")
    collection = chroma_client.get_collection(name="bells")

    model = GigaChat(
        credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOmY0NDcxNTZiLWIzOWUtNGUzYy05NTI1LTEyNjMyNjYxODBmNw==",
        scope="GIGACHAT_API_PERS",
        model="GigaChat-Max",
        verify_ssl_certs=False,
    )

    vectorstore = Chroma(
        client=chroma_client,
        collection_name="bells",
        embedding_function= GigaChatEmbeddings(
            credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOmY0NDcxNTZiLWIzOWUtNGUzYy05NTI1LTEyNjMyNjYxODBmNw==",
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
        )
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )

    message = """
    Отвечай на вопросы только с помощью полученного контекста.
    
    {question}
    
    Контекст:
    {context}
    """

    prompt = ChatPromptTemplate.from_messages([("human", message)])

    rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | model

    response = rag_chain.invoke(query)

    return response.content











