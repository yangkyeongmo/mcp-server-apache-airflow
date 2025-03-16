.PHONY: run build publish lint format

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
