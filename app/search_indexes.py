from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Bell
from gigachat import GigaChat
import json
import hashlib


@registry.register_document
class BellDocument(Document):
    # Поля Elasticsearch
    id_bell = fields.IntegerField(attr='id_bell')
    datetime_bell = fields.DateField()
    call_duration = fields.IntegerField()
    text_transcript = fields.TextField(attr='text_transripct')
    keywords = fields.KeywordField(attr='keywords_field', multi=True)

    class Index:
        name = 'bells'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'russian': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase']
                    }
                }
            }
        }

    class Django:
        model = Bell
        fields = []

    def prepare_keywords_field(self, instance):
        """Подготовка ключевых слов для индексации"""
        text = instance.text_transripct or ''
        if text:
            words = [word.lower() for word in text.split() if len(word) > 3]
            return list(set(words))[:10]  # Удаляем дубли и берем топ-10
        return []

    @classmethod
    def giga_search(cls, prompt, limit=5):
        """Гибридный поиск через GigaChat"""
        # 1. Предварительный поиск в Elasticsearch
        basic_results = cls.search().query(
            'multi_match',
            query=prompt,
            fields=['text_transcript^3', 'keywords'],
            fuzziness='AUTO'
        )[:20].execute()

        if not basic_results:
            return []

        # 2. Подготовка данных для GigaChat
        dialogs = [
            {
                "id": hit.meta.id,
                "text": hit.text_transcript,
                "keywords": hit.keywords
            }
            for hit in basic_results
        ]

        # 3. Запрос к GigaChat
        giga = GigaChat(credentials="YTFjOGUzYWQtY2ZjYS00MjAzLTk5YzctMGE4MDc1NzBmODBiOjM0NDMxYTZjLTJjODEtNDViMS05YzA1LTVlNzViMWQ5OTVhMg==", verify_ssl_certs=False)

        try:
            response = giga.chat(
                f"""Анализируй телефонные диалоги и возвращай JSON с релевантными результатами.

                Запрос пользователя: {prompt}

                Критерии анализа:
                - Соответствие смыслу запроса
                - Учет контекста диалога
                - Важность ключевых слов

                Диалоги для анализа: {json.dumps(dialogs, ensure_ascii=False)}

                Формат ответа:
                {{
                    "results": [
                        {{
                            "id": "идентификатор",
                            "relevance_score": 0-1,
                            "reason": "обоснование"
                        }}
                    ]
                }}"""
            )

            analyzed = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"GigaChat error: {str(e)}")
            analyzed = {"results": []}

        # 4. Формирование результатов
        results = []
        for item in analyzed.get("results", [])[:limit]:
            original = next((hit for hit in basic_results if hit.meta.id == item["id"]), None)
            if original:
                results.append({
                    "id": original.meta.id,
                    "call_id": original.id_bell,
                    "text": original.text_transcript,
                    "datetime": original.datetime_bell,
                    "score": item.get("relevance_score", 0),
                    "reason": item.get("reason", "")
                })

        return sorted(results, key=lambda x: x["score"], reverse=True)