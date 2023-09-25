from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class Report(BaseModel):
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


class RadisReport(BaseModel):
    document_id: str
    pacs_aet: str
    pacs_name: str
    patient_id: str
    patient_birth_date: date
    patient_sex: Literal["M", "F", "O"]
    study_instance_uid: str
    accession_number: str
    study_description: str
    study_datetime: datetime
    modalities_in_study: list[str]
    series_instance_uid: str
    sop_instance_uid: str
    body: str
