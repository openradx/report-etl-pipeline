"""Checks of the partition definitions and the schedules derived from them."""

import radis_etl_tkhd
from radis_etl_tkhd.partitions import collect_report_partitions_def, revised_report_partitions_def

TIMEZONE = "Europe/Berlin"


def test_partitions_are_defined_in_local_time() -> None:
    assert collect_report_partitions_def.timezone == TIMEZONE
    assert revised_report_partitions_def.timezone == TIMEZONE


def test_schedules_run_in_local_time() -> None:
    for name in ["collect_reports_job_schedule", "revise_reports_job_schedule"]:
        assert radis_etl_tkhd.defs.resolve_schedule_def(name).execution_timezone == TIMEZONE
