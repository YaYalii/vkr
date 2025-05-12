from elasticsearch_dsl import Document, Text, Date, connections
from app.models import Bell

# Устанавливаем соединение с Elasticsearch
connections.create_connection(hosts=['http://elasticsearch:9200'])

class BellDocument(Document):
    name = Text()
    created_at = Date()

    class Index:
        name = 'bells'

    def prepare(self, instance):
        self.meta.id = instance.id
        self.name = instance.name
        self.created_at = instance.created_at
