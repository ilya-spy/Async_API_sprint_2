# Добавление нового пайплайна

1. Добавить необходимые модели в `src/etl/entities.py`
2. Добавить producer в `src/etl/producers.py`
3. Добавить новый enricher в `src/etl/enrichers` и зарегистрировать его в `entichers/__init__.py`
4. Добавить новый transformer в `src/etl/transformers.py`
5. Добавить новую функцию создания пайплайна в `src/indexer.py` и зарегисрировать в `pipelines_builders`