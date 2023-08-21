from datetime import datetime

from dagster import AssetExecutionContext, HourlyPartitionsDefinition, asset


@asset(partitions_def=HourlyPartitionsDefinition(start_date=datetime(2023, 8, 21)))
def fetch_sr_from_adit(context: AssetExecutionContext) -> None:
    partition_date_str = context.asset_partition_key_for_output()
    print("adta", partition_date_str)


# TODO:
# - asset to fetch reference
# - asset to extract report
# - asset to put data into radis
