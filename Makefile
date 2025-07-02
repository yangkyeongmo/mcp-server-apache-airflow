.PHONY: run build publish lint format test test-coverage test-fast test-main test-server test-dag

PYTHON=uv run --env-file .env python

PARAMS=
run:
	$(PYTHON) src $(PARAMS)
run-sse:
	$(PYTHON) src --transport sse $(PARAMS)
build:
	uv build
publish:
	uv publish
lint:
	$(PYTHON) -m ruff check . --fix
format:
	$(PYTHON) -m ruff format .
test:
	$(PYTHON) -m pytest test/ -v
test-coverage:
	$(PYTHON) -m pytest test/ --cov=src --cov-report=term-missing --cov-report=html
test-fast:
	$(PYTHON) -m pytest test/ -x -v
test-main:
	$(PYTHON) -m pytest test/test_main.py -v
test-server:
	$(PYTHON) -m pytest test/test_server.py -v
test-dag:
	$(PYTHON) -m pytest test/test_dag.py -v
