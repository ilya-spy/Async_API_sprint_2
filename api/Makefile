.PHONY: run
.PHONY: f_test

run:
	PYTHONPATH=$(shell pwd)/src gunicorn -c src/core/gunicorn.py main:app

prep:
	pip install --no-cache-dir -r tests/ 11requirements.``txt
	PYTHONPATH=$(shell pwd)/tests python3 tests/utils/wait_for_es.py
	PYTHONPATH=$(shell pwd)/tests python3 tests/utils/wait_for_redis.py

f_test:
	PYTHONPATH=$(shell pwd)/src:$(shell pwd)/tests; \
	PATH=/home/web/.local/bin:${PATH}; \
	pytest tests/functional/src

test: prep f_test
