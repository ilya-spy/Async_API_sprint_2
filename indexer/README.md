# Добавление нового пайплайна

1. Добавить необходимые модели в `src/entities`
2. Добавить producer в `src/producers и зарегистрировать его в `src/producers/__init__.py`
3. Добавить новый enricher в `src/enrichers` и зарегистрировать его в `src/entichers/__init__.py`
4. Добавить новый transformer в `src/transformers.py` и зарегистрировать его в `src/transformers/__init__.py`
5. Добавить новую функцию создания пайплайна в `src/main.py` и зарегисрировать в `pipelines_builders`