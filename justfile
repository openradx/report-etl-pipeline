# Run `just` to list the available recipes.

project := "radis_etl_tkhd"
compose := "env UID=$(id -u) GID=$(id -g) docker compose -f compose/docker-compose.base.yml"

[private]
default:
    @just --list --unsorted

# Install the dependencies (incl. dev tools) into .venv
sync:
    uv sync

# Lint the source code (ruff)
lint:
    uv run ruff check .
    uv run ruff format --check .

# Format the source code and fix lint errors (ruff)
format:
    uv run ruff format .
    uv run ruff check --fix .

# Type check the source code (pyright)
typecheck:
    uv run pyright

# Run the tests (pytest), extra arguments are passed on
test *args:
    uv run pytest {{ args }}

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Show outdated dependencies
outdated:
    uv tree --outdated --depth 1

# Build and start the Dagster stack in Docker (env: dev or prod)
up env="dev":
    {{ compose }} -f compose/docker-compose.{{ env }}.yml -p {{ project }}_{{ env }} up --build --detach

# Stop the Dagster stack (env: dev or prod)
down env="dev":
    {{ compose }} -f compose/docker-compose.{{ env }}.yml -p {{ project }}_{{ env }} down

# Follow the logs of the Dagster stack (env: dev or prod)
logs env="dev":
    {{ compose }} -f compose/docker-compose.{{ env }}.yml -p {{ project }}_{{ env }} logs --follow

# Delete all Dagster instance data except dagster.yaml (env: dev or prod)
[confirm("This deletes all runs and artifacts in the dagster_home folder. Continue?")]
clean-dagster-home env="dev":
    find dagster_home_{{ env }} -mindepth 1 -maxdepth 1 ! -name dagster.yaml -exec rm -rf {} +
