from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, field_serializer, field_validator


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
    created: datetime

    @field_validator("patient_birth_date")
    @classmethod
    def validate_patient_birth_date(cls, value: str | date):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

    @field_validator("study_datetime")
    @classmethod
    def validate_study_datetime(cls, value: str | datetime):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    @field_serializer("patient_birth_date")
    def serialize_patient_birth_date(self, value: date):
        return value.isoformat()

    @field_serializer("study_datetime")
    def serialize_study_datetime(self, value: datetime):
        return value.isoformat()


class SanitizedReport(AditReport):
    document_id: str
    language: str
    groups: list[int]
    links: list[str]
    body_sanitized: str
