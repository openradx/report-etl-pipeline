from pathlib import Path

from invoke.context import Context
from invoke.tasks import task

dagster_home = Path(__file__).parent.absolute()


@task
def dagster_dev(ctx: Context):
    ctx.run(f"export DAGSTER_HOME={dagster_home} && dagster dev")


@task
def show_outdated(ctx: Context):
    """Show outdated dependencies"""
    ctx.run("poetry show --outdated --top-level")
