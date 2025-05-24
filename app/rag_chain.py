from gigachat import GigaChat
#
# giga = GigaChat(
#    credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOmY0NDcxNTZiLWIzOWUtNGUzYy05NTI1LTEyNjMyNjYxODBmNw==",
#     verify_ssl_certs=False
# )
#
# response = giga.get_token()
#
# print(response)

import requests

# access_token = 'eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.ju8tHA2qIXNAy9kDKKwPr-YxvBtZ8g-1Xgo0FjJucGHEDe6xHqhkTfUYHJDRfGwqxXEFk5ctu3J2fVbYwqIN6vbLlupZk-waN4ZbAmn8q_7ZvXNnCQ-xmPxfy7CTzxCOo_-R5z3QsgJvCoKq5xsEeKu-mWPg3Xj7c9Z78iI7J0kkYGrdbi-thT0gfEjGDJgPKPmllt9IIDL3g4ktonx8VP0I11IZorgzuHHbubdEY2uMMruxqrxtzONncsfA0559EgsziM7rGiX3UatFA6UoLLNd-P8QMC1aLmH99y7YFyHm9hkfca2Frwhf9AAZb-DrLAK6vVt1PPvsQ-fuvc7fAg.hrqt3dLue-UBdFywCIaCCw.Y70uerfdABsy-EFP8E0lYcY2NlJQre3V5dpotcLZ_Th8G_U2WqgH2_s81y7GWsqYz3KnRTq9jh4wn9don25O_ngmrCzeTJp3_oj7_LL-ypUmaBpzk_PIeJ7-Kejwyw5VmT7lfTrYGXZFl47g5Zi8rbXR2gRWPeKFuzUspEeGn0mVuEDzwV5_mOBQITtUJu_dKnNlLbbTbFvQgsVb-_CFy1oJ6RJy53pdDNQKy6OH2qZ4XlF6Dpf3gzCrbIyK_lMZ0KchsrRlFia7ksM4Asx061i6AbQnPuhb9vAXaXp8LIFplx1_BFKs-BT7yUHjYtFQ6iPKRuO5gQu8duHl5W1TzbwJezTlVlkCqinMwCzNSxSCHSp-6mywS3WjmOJ_NLWiq1gfTZEwh_w7pc165aFumoysdkSszoimU94hbnr8U1hUSArT1kiebRfzHMvzeg8wi74VHwDxbgfybnrLcK5HD8l0MhAzHZa9569f70vOPU4GNjPOBFviJCuHqscukQA0Kk46d6oQsg74IJSczEvlw-tTnFduZHuaZdKsAEy7YMVEW0ijD_cnDOKU7yJof-8Sb9dRFitEMrWl_dolpdTGi6ThA6nUSBbOcBwzaYnViW6Kz-Pb1SvTKPM7AH7vEtQT8WZsHNNV33PUo48R45BrJqfhn06fuahXnIe6oWFLM8lDS5jBqh7IPwCccueEJ_uxBt_trFOrsruKYtEBoCfLBUxYc2yCLhAAmqMRmVfckmM.VJq8PlklnAh8RuJc6XDhPVnn4TnyIY8hFJISJELNRrQ'
#
#
#
# url = "https://gigachat.devices.sberbank.ru/api/v1/models"
#
# giga = GigaChat(
#     credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOmY0NDcxNTZiLWIzOWUtNGUzYy05NTI1LTEyNjMyNjYxODBmNw==",
#     verify_ssl_certs=False
# )
#
# response = giga.embeddings(["Текст"])
#
# print(response)
#
#
#
#
#

from elasticsearch import Elasticsearch
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_gigachat.embeddings import GigaChatEmbeddings
from langchain_community.vectorstores import ElasticVectorSearch
from langchain_gigachat.chat_models import GigaChat
import base64
import os


def run_rag_query(question: str) -> str:
    # 1. Настройка аутентификации GigaChat
    client_id = "a1c8e3ad-cfca-4203-99c7-0a807570f80b"
    client_secret = "20f12b93-1226-4e08-8a14-51148e3cfe4f"  # Замените на ваш реальный client_secret
    autorization_key = "YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOmY0NDcxNTZiLWIzOWUtNGUzYy05NTI1LTEyNjMyNjYxODBmNw=="
    # Правильное формирование credentials
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    # Путь к сертификату (должен существовать)
    cert_path = os.path.join(os.path.dirname(__file__), "russian_trusted_root_ca.cer")

    try:
        # 2. Инициализация GigaChat
        llm = GigaChat(
            credentials=autorization_key,
            verify_ssl_certs=False
        )

        # 3. Инициализация эмбеддингов
        embedding_model = GigaChatEmbeddings(
            credentials=autorization_key,
            verify_ssl_certs=False
        )

        # 4. Настройка Elasticsearch
        vectorstore = ElasticVectorSearch(
            elasticsearch_url="http://elasticsearch:9200",
            index_name="bells",
            embedding=embedding_model
        )

        # 5. Настройка цепочки QA
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="Контекст:\n{context}\n\nВопрос: {question}\nОтвет:"
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": prompt}
        )

        return qa_chain.invoke({"query": question})["result"]

    except Exception as e:
        raise Exception(f"Ошибка при выполнении запроса: {str(e)}")




# from elasticsearch import Elasticsearch
# from langchain.chains.retrieval_qa.base import RetrievalQA
# from langchain_core.prompts import PromptTemplate
# from langchain_gigachat.embeddings import GigaChatEmbeddings
# from langchain_community.vectorstores import ElasticVectorSearch
# from langchain_gigachat.chat_models import GigaChat
# import urllib3
# import base64
#
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# def run_rag_query(question: str) -> str:

    # es_client = Elasticsearch("http://elasticsearch:9200")  # имя контейнера в docker-compose
    #
    # credentials = "a1c8e3ad-cfca-4203-99c7-0a807570f80b"
    # encoded_credentials = base64.b64encode(credentials.encode()).decode()
    #
    # client_secret = "a1c8e3ad-cfca-4203-99c7-0a807570f80b"
    # credentials = "YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOjIwZjEyYjkzLTEyMjYtNGUwOC04YTE0LTUxMTQ4ZTNjZmU0Zg"
    #
    # embedding_model = GigaChatEmbeddings(credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOjIwZjEyYjkzLTEyMjYtNGUwOC04YTE0LTUxMTQ4ZTNjZmU0Zg==",
    #                                      ca_bundle_file="russian_trusted_root_ca.cer")
    #
    # vectorstore = ElasticVectorSearch(
    #     elasticsearch_url="http://localhost:9200",
    #     index_name="bells",
    #     embedding=embedding_model,
    #     ssl_verify=None
    #     # text_field="text_transcript"
    # )
    #
    # llm = GigaChat(
    # credentials=credentials,
    # ca_bundle_file="russian_trusted_root_ca.cer"
    # )
    #
    # prompt = PromptTemplate(
    #     input_variables=["context", "question"],
    #     template="Контекст:\n{context}\n\nВопрос: {question}\nОтвет:"
    # )
    #
    # qa_chain = RetrievalQA.from_chain_type(
    #     llm=llm,
    #     chain_type="stuff",
    #     retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    #     chain_type_kwargs={"prompt": prompt}
    # )
    #
    # return qa_chain.run(question)
# from gigachat import GigaChat
#
# # Используйте ключ авторизации, полученный в личном кабинете, в проекте GigaChat API.
# with GigaChat(credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOjIwZjEyYjkzLTEyMjYtNGUwOC04YTE0LTUxMTQ4ZTNjZmU0Zg==",
#               ca_bundle_file="C:\pycharm\\russian_trusted_root_ca.cer") as giga:
#     response = giga.chat("Какие факторы влияют на стоимость страховки на дом?")
#     print(response.choices[0].message.content)