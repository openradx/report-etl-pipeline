from datetime import datetime

from dagster import (
    DailyPartitionsDefinition,
)

# The partitions (and the schedules derived from them) use the local time of the PACS, so a
# partition covers a calendar day as seen by the PACS and is complete at local midnight.
TIMEZONE = "Europe/Berlin"

# `start_date` is the first day the backfill will start.
collect_report_partitions_def = DailyPartitionsDefinition(
    start_date=datetime(2014, 1, 1), timezone=TIMEZONE
)

# `end_offset` shifts the last available partition, which is the one a schedule built from
# this partitions definition materializes. Without an offset that is the previous day, with
# an offset of -7 it is the day 8 days before.
revised_report_partitions_def = DailyPartitionsDefinition(
    start_date=datetime(2024, 5, 1), end_offset=-7, timezone=TIMEZONE
)
