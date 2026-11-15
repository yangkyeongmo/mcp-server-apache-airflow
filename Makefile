.PHONY: run build publish lint lint-fix format typecheck test test-contract test-integration

PYTHON=uv run --env-file .env python
UV=uv run

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
	$(UV) ruff format --check .
	$(UV) ruff check .
lint-fix:
	$(UV) ruff check . --fix
	$(UV) ruff format .
format:
	$(UV) ruff format .
typecheck:
	$(UV) mypy src
test:
	$(UV) pytest test/ -v -m "not integration"
test-contract:
	$(UV) pytest test/contract -v
test-integration:
	$(UV) pytest test/ -v -m integration
