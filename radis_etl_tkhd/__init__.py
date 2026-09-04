import os

from dagster import (
    AssetSelection,
    DefaultScheduleStatus,
    Definitions,
    EnvVar,
    build_schedule_from_partitioned_job,
    define_asset_job,
)

from . import assets, io_managers, resources

collect_reports_job = define_asset_job(
    name="collect_reports_job",
    selection=AssetSelection.groups("collected_reports"),
)

revise_reports_job = define_asset_job(
    name="revise_reports_job",
    selection=AssetSelection.groups("revised_reports"),
)

# Schedules start automatically in production only (DAGSTER_DEPLOYMENT=prod is set by the
# production Compose file). Elsewhere they stay stopped until turned on in the Dagster UI.
schedule_status = (
    DefaultScheduleStatus.RUNNING
    if os.getenv("DAGSTER_DEPLOYMENT") == "prod"
    else DefaultScheduleStatus.STOPPED
)

# Schedule every day at 2 AM (UTC) / 3 AM (MEZ) / 4 AM (MESZ)
collect_reports_schedule = build_schedule_from_partitioned_job(
    collect_reports_job, hour_of_day=2, default_status=schedule_status
)

# Schedule every day at 3 AM (UTC) / 4 AM (MEZ) / 5 AM (MESZ)
revise_reports_schedule = build_schedule_from_partitioned_job(
    revise_reports_job, hour_of_day=3, default_status=schedule_status
)

defs = Definitions(
    assets=assets.all_assets,
    jobs=[collect_reports_job, revise_reports_job],
    resources={
        "io_manager": io_managers.ReportIOManagerFactory(
            artifacts_dir=EnvVar("ARTIFACTS_DIR"),
        ),
        "adit": resources.AditResource(
            host=EnvVar("ADIT_HOST"),
            auth_token=EnvVar("ADIT_AUTH_TOKEN"),
            ca_bundle=EnvVar("CA_BUNDLE"),
        ),
        "radis": resources.RadisResource(
            radis_host=EnvVar("RADIS_HOST"),
            auth_token=EnvVar("RADIS_AUTH_TOKEN"),
            ca_bundle=EnvVar("CA_BUNDLE"),
        ),
    },
    schedules=[collect_reports_schedule, revise_reports_schedule],
)
