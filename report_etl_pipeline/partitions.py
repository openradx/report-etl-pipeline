from datetime import datetime

from dagster import (
    DailyPartitionsDefinition,
)

# `start_date` is the first day the backfill will start.
collect_report_partitions_def = DailyPartitionsDefinition(start_date=datetime(2014, 1, 1))

# `offset` is relevant when an asset with this partition is scheduled. Then the partition
# with the offset will be evaluated (in our case, 7 days before when the schedule is executed).
revised_report_partitions_def = DailyPartitionsDefinition(
    start_date=datetime(2024, 5, 1), end_offset=-7
)
