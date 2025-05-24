from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry  # Добавляем импорт registry
from .models import Bell

@registry.register_document  # Регистрируем документ
class BellDocument(Document):
    class Index:
        name = 'bells'  # Имя индекса в Elasticsearch
        settings = {
            'number_of_shards': 1,  # Количество шардов
            'number_of_replicas': 0  # Количество реплик
        }

    # Явно указываем поля для индексации
    id_bell = fields.IntegerField(attr='id_bell')
    datetime_bell = fields.DateField()
    call_duration = fields.IntegerField()
    text_transcript = fields.TextField(attr='text_transripct')  # Используем attr для связи с полем модели

    class Django:
        model = Bell  # Указываем модель
        fields = []  # Можно оставить пустым, так как поля объявлены выше

    def get_queryset(self):
        """Оптимизация запроса к БД."""
        return super().get_queryset().select_related('id_employee_fk')
# from django_elasticsearch_dsl import Document, fields
# from django_elasticsearch_dsl.registries import registry
# from .models import Bell
# from sentence_transformers import SentenceTransformer
# import numpy as np
#
# # Инициализация модели для эмбеддингов (вынесено в отдельный модуль для переиспользования)
# embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
#
#
# @registry.register_document
# class BellDocument(Document):
#     # Основные поля
#     id_bell = fields.IntegerField(attr='id_bell')
#     datetime_bell = fields.DateField()
#     call_duration = fields.IntegerField()
#     text_transcript = fields.TextField(
#         attr='text_transripct',
#         analyzer='russian',  # Добавляем русский анализатор
#         fields={
#             'keyword': fields.KeywordField(),  # Для точного match
#             'stemmed': fields.TextField(analyzer='russian')  # Для поиска с учетом морфологии
#         }
#     )
#
#     # Новые поля для векторного поиска
#     embedding = fields.DenseVectorField(
#         dims=384,  # Размерность модели sentence-transformers
#         attr='embedding_field'  # Специальный метод для получения embedding
#     )
#
#     # Метаданные для фильтрации
#     employee_id = fields.IntegerField(attr='id_employee_fk_id')
#     department = fields.KeywordField(attr='id_employee_fk.department')  # Пример связи
#
#     class Index:
#         name = 'bells'
#         settings = {
#             'number_of_shards': 1,
#             'number_of_replicas': 0,
#             'analysis': {  # Конфигурация анализатора для русского языка
#                 'analyzer': {
#                     'russian': {
#                         'type': 'custom',
#                         'tokenizer': 'standard',
#                         'filter': [
#                             'lowercase',
#                             'russian_morphology',
#                             'english_morphology'
#                         ]
#                     }
#                 }
#             }
#         }
#
#     class Django:
#         model = Bell
#         fields = []  # Все необходимые поля объявлены выше
#
#         # Оптимизация связанных полей
#         related_models = ['Employee']  # Укажите вашу модель Employee
#
#     def get_queryset(self):
#         """Оптимизированный запрос с предзагрузкой связанных данных"""
#         return super().get_queryset().select_related('id_employee_fk')
#
#     def get_instances_from_related(self, related_instance):
#         """Обновление индекса при изменении связанных моделей"""
#         if isinstance(related_instance, Employee):  # Укажите вашу модель Employee
#             return related_instance.bell_set.all()  # Укажите правильное имя related_name
#         return None
#
#     def prepare_embedding_field(self, instance):
#         """Подготовка векторного представления текста"""
#         text = instance.text_transripct or ''  # Исправьте опечатку в вашем поле
#         if text:
#             return embedding_model.encode(text).tolist()
#         return None
#
#     @classmethod
#     def search_vector(cls, query_text, limit=10):
#         """Поиск по семантическому сходству"""
#         query_embedding = embedding_model.encode(query_text).tolist()
#
#         return cls.search().query(
#             'script_score',
#             query={'match_all': {}},
#             script={
#                 'source': 'cosineSimilarity(params.query_vector, "embedding") + 1.0',
#                 'params': {'query_vector': query_embedding}
#             }
#         )[:limit]
#
#     @classmethod
#     def hybrid_search(cls, query_text, limit=10):
#         """Гибридный поиск (семантический + текстовый)"""
#         # Векторный поиск
#         vector_results = cls.search_vector(query_text, limit)
#
#         # Текстовый поиск
#         text_results = cls.search().query(
#             'multi_match',
#             query=query_text,
#             fields=['text_transcript', 'text_transcript.stemmed'],
#             fuzziness='AUTO'
#         )[:limit]
#
#         # Объединение результатов (можно усложнить логику)
#         combined = {}
#         for idx, result in enumerate(vector_results):
#             combined[result.meta.id] = {
#                 'result': result,
#                 'score': result.meta.score * 0.7  # Вес векторного поиска
#             }
#
#         for idx, result in enumerate(text_results):
#             if result.meta.id in combined:
#                 combined[result.meta.id]['score'] += 0.3  # Вес текстового поиска
#             else:
#                 combined[result.meta.id] = {
#                     'result': result,
#                     'score': 0.3
#                 }
#
#         # Сортировка по комбинированному score
#         sorted_results = sorted(
#             combined.values(),
#             key=lambda x: x['score'],
#             reverse=True
#         )
#
#         return [item['result'] for item in sorted_results[:limit]]