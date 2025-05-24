from django.core.management.base import BaseCommand
from app.models import Bell
from chromadb import PersistentClient
from chromadb.config import Settings
from gigachat import GigaChat

class Command(BaseCommand):
    help = "Генерация и импорт embedding из Bell в ChromaDB"

    def handle(self, *args, **kwargs):
        giga = GigaChat(credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOmY0NDcxNTZiLWIzOWUtNGUzYy05NTI1LTEyNjMyNjYxODBmNw==", verify_ssl_certs=False)
        chroma_client = PersistentClient(path="/app/chroma_data")
        collection = chroma_client.get_or_create_collection(name="bells")

        bells = Bell.objects.all()
        for bell in bells:
            if not bell.text_transripct:
                continue

            embedding = giga.embeddings([bell.text_transripct]).data[0].embedding
            bell.embedding = embedding
            bell.save()

            collection.add(
                documents=[bell.text_transripct],
                metadatas=[{"id_bell": bell.id_bell}],
                embeddings=[embedding],
                ids=[str(bell.id_bell)]
            )
            self.stdout.write(f"✔ Added Bell ID {bell.id_bell}")
