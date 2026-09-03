from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class AditReport(BaseModel):
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
    body_original: str
    created_at: datetime


class SanitizedReport(AditReport):
    document_id: str
    language: str
    groups: list[int]
    pacs_link: str
    body_sanitized: str


class RevisedReport(SanitizedReport):
    revision_type: Literal["added", "changed"] | None
    revised_at: datetime | None
