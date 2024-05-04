from datetime import datetime

from dagster import (
    DailyPartitionsDefinition,
)

collect_report_partitions_def = DailyPartitionsDefinition(start_date=datetime(2012, 1, 1))
