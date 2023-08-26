from datetime import date, datetime
from typing import Literal, TypedDict


class Report(TypedDict):
    pacs_aet: str
    pacs_name: str
    patient_id: str
    patient_birth_date: str
    patient_sex: Literal["M", "F", "O"]
    study_instance_uid: str
    accession_number: str
    study_description: str
    study_date: str
    study_time: str
    modalities_in_study: list[str]
    series_instance_uid: str
    sop_instance_uid: str
    body: str


class ReportWithReferences(Report):
    references: list[str]


class RadisReport(TypedDict):
    pacs_aet: str
    pacs_name: str
    patient_id: str
    patient_birth_data: date
    patient_sex: Literal["M", "F", "O"]
    study_instance_uid: str
    accession_number: str
    study_description: str
    study_datetime: datetime
    modalities_in_study: list[str]
    series_instance_uid: str
    sop_instance_uid: str
    body: str
