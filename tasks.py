from pathlib import Path

from invoke.context import Context
from invoke.tasks import task

dagster_home = Path(__file__).parent.absolute()


@task
def start_dev(ctx: Context):
    ctx.run(f"export DAGSTER_HOME={dagster_home} && dagster dev")
