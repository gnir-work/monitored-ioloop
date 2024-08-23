install:
	poetry install --with dev

format:
	poetry run ruff format
	poetry run ruff check --fix --unsafe-fixes .

lint-formatters:
	poetry run ruff format --check
	poetry run ruff check .

lint-static-code-analysis:
	poetry run mypy .

lint: lint-formatters lint-static-code-analysis

pre-commit: format lint-static-code-analysis

test:
	poetry run pytest