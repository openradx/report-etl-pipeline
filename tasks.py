from pathlib import Path

from invoke.context import Context
from invoke.runners import Result
from invoke.tasks import task

###
# Helper functions
###


def run_cmd(ctx: Context, cmd: str, silent=False) -> Result:
    if not silent:
        print(f"Running: {cmd}")

    hide = True if silent else None

    result = ctx.run(cmd, pty=True, hide=hide)
    assert result and result.ok
    return result


###
# Tasks
###


@task
def dagster_dev(ctx: Context):
    """Start Dagster for development"""
    if not Path("./.env").is_file():
        raise ValueError("Missing .env file for development")

    dagster_home = Path(__file__).parent.absolute() / "dagster_home"
    run_cmd(ctx, f"export DAGSTER_HOME={dagster_home} && dagster dev")


@task
def compose_up(
    ctx: Context,
    no_build: bool = False,
):
    """Start Dagster container (production environment)"""
    build_opt = "--no-build" if no_build else "--build"
    cmd = f"docker compose -f docker.compose.yaml up {build_opt} --detach"
    run_cmd(ctx, cmd)


@task
def compose_down(
    ctx: Context,
    cleanup: bool = False,
):
    """Stop Dagster container (production environment)"""
    cmd = "docker compose -f docker.compose.yaml down"
    if cleanup:
        cmd += " --remove-orphans --volumes"
    run_cmd(ctx, cmd)


@task
def show_outdated(ctx: Context):
    """Show outdated dependencies"""
    ctx.run("poetry show --outdated --top-level")
