.PHONY: run build publish lint lint-fix format typecheck test test-contract test-integration test-e2e-mcp dump-mcp-tools mcp-compat airflow-up airflow-down

PYTHON=uv run python

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
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m ruff check .
lint-fix:
	$(PYTHON) -m ruff check . --fix
	$(PYTHON) -m ruff format .
format:
	$(PYTHON) -m ruff format .
typecheck:
	$(PYTHON) -m mypy src
test:
	$(PYTHON) -m pytest test/ -m "not integration and not e2e_mcp" -v
test-contract:
	$(PYTHON) -m pytest test/contracts -v
test-integration:
	AIRFLOW_HOST=$${AIRFLOW_HOST:-http://127.0.0.1:8080} \
	AIRFLOW_USERNAME=$${AIRFLOW_USERNAME:-airflow} \
	AIRFLOW_PASSWORD=$${AIRFLOW_PASSWORD:-airflow} \
	$(PYTHON) -m pytest test/ -m integration -v
test-e2e-mcp:
	AIRFLOW_HOST=$${AIRFLOW_HOST:-http://127.0.0.1:8080} \
	AIRFLOW_USERNAME=$${AIRFLOW_USERNAME:-airflow} \
	AIRFLOW_PASSWORD=$${AIRFLOW_PASSWORD:-airflow} \
	$(PYTHON) -m pytest test/mcp/test_protocol_e2e.py -m e2e_mcp -v
dump-mcp-tools:
	$(PYTHON) scripts/dump_mcp_tools.py --out test/mcp/tools_snapshot.json
mcp-compat:
	bash scripts/mcp_compat_ci.sh
airflow-up:
	docker compose -f test/integration/docker-compose.yaml up -d --wait
airflow-down:
	docker compose -f test/integration/docker-compose.yaml down -v
