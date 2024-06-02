from dagster import (
    AssetSelection,
    Definitions,
    EnvVar,
    build_schedule_from_partitioned_job,
    define_asset_job,
)

from . import assets, io_managers, partitions, resources

collect_reports_job = define_asset_job(
    name="collect_reports_job",
    selection=AssetSelection.groups("collected_reports"),
    partitions_def=partitions.collect_report_partitions_def,
)

revise_reports_job = define_asset_job(
    name="revise_reports_job",
    selection=AssetSelection.groups("revised_reports"),
    partitions_def=partitions.revised_report_partitions_def,
)

# Schedule every day at 2 AM (UTC) / 3 AM (MEZ) / 4 AM (MESZ)
collect_reports_schedule = build_schedule_from_partitioned_job(collect_reports_job, hour_of_day=2)

# Schedule every day at 3 AM (UTC) / 4 AM (MEZ) / 5 AM (MESZ)
revise_reports_schedule = build_schedule_from_partitioned_job(revise_reports_job, hour_of_day=3)

defs = Definitions(
    assets=assets.all_assets,
    jobs=[collect_reports_job],
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
