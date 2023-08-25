from datetime import date, time
from typing import Literal, TypedDict


class Report(TypedDict):
    pacs_aet: str
    pacs_name: str
    patient_id: str
    patient_birth_date: date
    patient_sex: Literal["M", "F", "O"]
    study_instance_uid: str
    accession_number: str
    study_description: str
    study_date: date
    study_time: time
    modalities_in_study: list[str]
    series_instance_uid: str
    sop_instance_uid: str
    references: list[str]
    body: str
