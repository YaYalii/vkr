from gigachat import GigaChat

giga = GigaChat(
   credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOmY0NDcxNTZiLWIzOWUtNGUzYy05NTI1LTEyNjMyNjYxODBmNw==",
   verify_ssl_certs=False
)

response = giga.embeddings(["Текст"])

print(response)