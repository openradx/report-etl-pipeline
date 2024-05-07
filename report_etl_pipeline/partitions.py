from datetime import datetime

from dagster import (
    DailyPartitionsDefinition,
)

collect_report_partitions_def = DailyPartitionsDefinition(start_date=datetime(2014, 1, 1))

revised_report_partitions_def = DailyPartitionsDefinition(
    start_date=datetime(2024, 5, 1), end_offset=-7
)
