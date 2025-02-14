build:
	uv run python -m build

publish:
	uv run python -m twine upload --config-file .pypirc dist/*
