from datetime import datetime

from dagster import (
    AssetExecutionContext,
    DailyPartitionsDefinition,
    asset,
)

from .resources import AditResource


@asset(partitions_def=DailyPartitionsDefinition(start_date=datetime(2020, 1, 1)))
def sr_datasets_from_synapse(context: AssetExecutionContext, adit: AditResource) -> list[str]:
    print("1", context.partition_key)
    print("2", context.partition_time_window)
    print("3", adit.auth_token)
    return ["xxx", "yyy", "zzz"]


@asset(partitions_def=DailyPartitionsDefinition(start_date=datetime(2020, 1, 1)))
def resport_data(sr_datasets_from_synapse: list[str]) -> None:
    print(sr_datasets_from_synapse)


# TODO:
# - asset to fetch reference
# - asset to extract report
# - asset to put data into radis
