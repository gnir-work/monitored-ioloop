TARGET_DIR = .
POETRY_GROUPS = dev,stress_test,code_quality,examples

install:
	poetry install --with ${POETRY_GROUPS} -E uvloop -E fastapi

format:
	poetry run ruff format ${TARGET_DIR}
	poetry run ruff check --fix --unsafe-fixes ${TARGET_DIR}

lint-formatters:
	poetry run ruff format --check ${TARGET_DIR}
	poetry run ruff check ${TARGET_DIR}

lint-static-code-analysis:
	poetry run mypy ${TARGET_DIR}

lint: lint-formatters lint-static-code-analysis

pre-commit: format lint-static-code-analysis

test:
	poetry run pytest --cov=monitored_ioloop -n auto tests

test-for-flakiness:
	poetry run pytest --cov=monitored_ioloop -n auto --count=10