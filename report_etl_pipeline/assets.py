from datetime import datetime

from dagster import (
    AssetExecutionContext,
    DailyPartitionsDefinition,
    asset,
)

from .resources import AditResource
from .types import Report


@asset(partitions_def=DailyPartitionsDefinition(start_date=datetime(2020, 1, 1)))
def reports_from_synapse(context: AssetExecutionContext, adit: AditResource) -> list[str]:
    time_window = context.partition_time_window
    datasets = adit.fetch_sr_from_synapse(time_window)

    report: Report = {
        "pacs_aet": "PACS_AET",
        "pacs_name": "PACS_NAME",
        "patient_id": "PATIENT_ID",
        "patient_birth_date": datetime(2020, 1, 1).date(),
        "patient_sex": "M",
        "study_instance_uid": "STUDY_INSTANCE_UID",
        "accession_number": "ACCESSION_NUMBER",
        "study_description": "STUDY_DESCRIPTION",
        "study_date": datetime(2020, 1, 1).date(),
        "study_time": datetime(2020, 1, 1).time(),
        "modalities_in_study": ["CT"],
        "series_instance_uid": "SERIES_INSTANCE_UID",
        "sop_instance_uid": "SOP_INSTANCE_UID",
        "references": [],
        "body": "foo,bar;zar",
    }
    return [report]


@asset(partitions_def=DailyPartitionsDefinition(start_date=datetime(2020, 1, 1)))
def reports_with_references(reports_from_synapse: list[str]) -> None:
    pass


# TODO:
# - asset to fetch reference
# - asset to extract report
# - asset to put data into radis
