import os
from pathlib import Path
from typing import Literal

from invoke.context import Context
from invoke.tasks import task

Environments = Literal["dev", "prod"]

stack_name_dev = "report_etl_pipeline_dev"
stack_name_prod = "report_etl_pipeline_prod"

project_dir = Path(__file__).resolve().parent
compose_dir = project_dir / "compose"

compose_file_base = compose_dir / "docker-compose.base.yml"
compose_file_dev = compose_dir / "docker-compose.dev.yml"
compose_file_prod = compose_dir / "docker-compose.prod.yml"

###
# Helper functions
###


def get_stack_name(env: Environments):
    if env == "dev":
        return stack_name_dev
    elif env == "prod":
        return stack_name_prod
    else:
        raise ValueError(f"Unknown environment: {env}")


def build_compose_cmd(env: Environments):
    base_compose_cmd = f"docker compose -f '{compose_file_base}'"
    stack_name = get_stack_name(env)
    if env == "dev":
        return f"{base_compose_cmd} -f '{compose_file_dev}' -p {stack_name}"
    elif env == "prod":
        return f"{base_compose_cmd} -f '{compose_file_prod}' -p {stack_name}"
    else:
        raise ValueError(f"Unknown environment: {env}")


###
# Tasks
###


@task
def compose_up(
    ctx: Context,
    env: Environments = "dev",
    port: int = 8000,
    no_build: bool = False,
):
    """Start pipeline in specified environment"""
    build_opt = "--no-build" if no_build else "--build"
    cmd: list[str] = []
    if port:
        if env == "dev":
            cmd.append(f"export DAGSTER_DEV_PORT={port} && ")
        elif env == "prod":
            cmd.append(f"export DAGSTER_NGINX_PORT={port} && ")
        else:
            raise ValueError(f"Unknown environment: {env}")

    cmd.append(f"{build_compose_cmd(env)} up {build_opt} --detach")
    ctx.run(" ".join(cmd), pty=True, env={"UID": str(os.getuid()), "GID": str(os.getgid())})


@task
def compose_down(
    ctx: Context,
    env: Environments = "dev",
    cleanup: bool = False,
):
    """Stop pipeline in specified environment"""
    cmd = f"{build_compose_cmd(env)} down"
    if cleanup:
        cmd += " --remove-orphans --volumes"
    ctx.run(cmd, pty=True, env={"UID": str(os.getuid()), "GID": str(os.getgid())})


@task
def show_outdated(ctx: Context):
    """Show outdated dependencies"""
    ctx.run("poetry show --outdated --top-level")
