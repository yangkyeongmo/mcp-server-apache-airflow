build:
	uv run python -m build
publish:
	uv run python -m twine upload --config-file .pypirc dist/*
lint:
	uv run ruff check . --fix
format:
	uv run ruff format .
