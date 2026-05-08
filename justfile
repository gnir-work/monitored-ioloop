target_dir := "."
groups := "dev,stress_test,code_quality,examples"
python_version := env("PYTHON_VERSION", "3.12")

# Install dependencies with optional groups
install groups=groups:
    #!/usr/bin/env bash
    if [ -n "{{groups}}" ]; then
        uv sync --python {{python_version}} --group $(echo {{groups}} | sed 's/,/ --group /g') --all-extras
    else
        uv sync --python {{python_version}} --all-groups --all-extras
    fi

# Format code using ruff
format target_dir=target_dir:
    uv run --python {{python_version}} ruff format {{target_dir}}
    uv run --python {{python_version}} ruff check --fix --unsafe-fixes {{target_dir}}

# Check code formatting (no fixes)
lint-formatters target_dir=target_dir:
    uv run --python {{python_version}} ruff format --check {{target_dir}}
    uv run --python {{python_version}} ruff check {{target_dir}}

# Run static code analysis with mypy
lint-static-code-analysis target_dir=target_dir:
    uv run --python {{python_version}} mypy {{target_dir}}

# Run all linting checks
lint target_dir=target_dir: (lint-formatters target_dir) (lint-static-code-analysis target_dir)

# Format and lint code (pre-commit hook)
pre-commit target_dir=target_dir: (format target_dir) (lint-static-code-analysis target_dir)

# Run tests with coverage
test:
    uv run --python {{python_version}} pytest --cov=monitored_ioloop -n auto tests

# Run tests multiple times to check for flakiness
test-for-flakiness:
    uv run --python {{python_version}} pytest --cov=monitored_ioloop -n auto --count=10