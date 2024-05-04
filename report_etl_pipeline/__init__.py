from dagster import (
    Definitions,
    EnvVar,
    build_schedule_from_partitioned_job,
    define_asset_job,
    load_assets_from_modules,
)

from . import assets, io_managers, partitions, resources

all_assets = load_assets_from_modules([assets])

collect_reports_job = define_asset_job(
    name="collect_reports_job", partitions_def=partitions.collect_report_partitions_def
)

# Schedule every day at 3 AM (UTC)
collect_reports_schedule = build_schedule_from_partitioned_job(collect_reports_job, hour_of_day=3)

defs = Definitions(
    assets=all_assets,
    jobs=[collect_reports_job],
    resources={
        "io_manager": io_managers.ReportIOManagerFactory(
            artifacts_dir=EnvVar("ARTIFACTS_DIR"),
        ),
        "adit": resources.AditResource(
            host=EnvVar("ADIT_HOST"),
            auth_token=EnvVar("ADIT_AUTH_TOKEN"),
        ),
        "radis": resources.RadisResource(
            radis_host=EnvVar("RADIS_HOST"),
            auth_token=EnvVar("RADIS_AUTH_TOKEN"),
        ),
    },
    schedules=[collect_reports_schedule],
)
