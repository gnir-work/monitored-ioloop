TARGET_DIR = .
GROUPS = dev,stress_test,code_quality,examples

install:
ifdef GROUPS
	uv sync --group $(shell echo $(GROUPS) | sed 's/,/ --group /g') --all-extras
else
	uv sync --all-groups --all-extras
endif

format:
	uv run ruff format ${TARGET_DIR}
	uv run ruff check --fix --unsafe-fixes ${TARGET_DIR}

lint-formatters:
	uv run ruff format --check ${TARGET_DIR}
	uv run ruff check ${TARGET_DIR}

lint-static-code-analysis:
	uv run mypy ${TARGET_DIR}

lint: lint-formatters lint-static-code-analysis

pre-commit: format lint-static-code-analysis

test:
	uv run pytest --cov=monitored_ioloop -n auto tests

test-for-flakiness:
	uv run pytest --cov=monitored_ioloop -n auto --count=10