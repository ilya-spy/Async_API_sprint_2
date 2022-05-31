.PHONY: run
run:
	PYTHONPATH=$(shell pwd)/src gunicorn -c $(shell pwd)/src/core/gunicorn.py main:app

