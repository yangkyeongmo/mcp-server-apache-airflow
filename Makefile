.PHONY: run build publish lint format

PYTHON=uv run --env-file .env python

PARAMS=
run:
	$(PYTHON) src $(PARAMS)
run-sse:
	$(PYTHON) src --transport sse $(PARAMS)
build:
	$(PYTHON) -m build
publish:
	$(PYTHON) -m twine upload --config-file .pypirc dist/*
lint:
	$(PYTHON) -m ruff check . --fix
format:
	$(PYTHON) -m ruff format .
