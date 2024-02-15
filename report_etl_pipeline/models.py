from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, field_serializer


class Report(BaseModel):
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

    @field_serializer("patient_birth_date")
    def serialize_patient_birth_date(self, patient_birth_date: date):
        return patient_birth_date.isoformat()

    @field_serializer("study_datetime")
    def serialize_study_datetime(self, study_datetime: datetime):
        return study_datetime.isoformat()

    def to_record(self):
        record = self.model_dump()
        record["modalities_in_study"] = "|".join(record["modalities_in_study"])
        return record

    @classmethod
    def from_record(cls, record):
        record["modalities_in_study"] = record["modalities_in_study"].split("|")
        return cls.model_validate(record)


class ReportWithLinks(Report):
    links: list[str]

    def to_record(self):
        record = super().to_record()
        record["links"] = "|".join(self.links)
        return record

    @classmethod
    def from_record(cls, record):
        record["modalities_in_study"] = record["modalities_in_study"].split("|")
        record["links"] = record["links"].split("|")
        return cls.model_validate(record)


class RadisReport(ReportWithLinks):
    document_id: str
    groups: list[int]
