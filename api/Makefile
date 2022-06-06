.PHONY: run
.PHONY: test

run:
	PYTHONPATH=$(shell pwd)/src gunicorn -c src/core/gunicorn.py main:app

test:
	PYTHONPATH=$(shell pwd)/tests python3 tests/utils/wait_for_es.py
	PYTHONPATH=$(shell pwd)/tests python3 tests/utils/wait_for_redis.py
	PYTHONPATH=$(shell pwd)/src:$(shell pwd)/tests pytest tests/functional/src
