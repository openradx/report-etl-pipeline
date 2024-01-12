from dagster import (
    Definitions,
    EnvVar,
    build_schedule_from_partitioned_job,
    define_asset_job,
    load_assets_from_modules,
)

from . import assets, io_managers, resources

all_assets = load_assets_from_modules([assets])

all_assets_job = define_asset_job(name="all_assets_job")

schedule = build_schedule_from_partitioned_job(all_assets_job, hour_of_day=1)

defs = Definitions(
    assets=all_assets,
    jobs=[all_assets_job],
    resources={
        "io_manager": io_managers.ReportIOManagerFactory(artifacts_dir=EnvVar("ARTIFACTS_DIR")),
        "adit": resources.AditResource(
            host=EnvVar("ADIT_HOST"),
            auth_token=EnvVar("ADIT_AUTH_TOKEN"),
        ),
    },
    schedules=[schedule],
)
