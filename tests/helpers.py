"""Test doubles and builders shared by the tests."""

from datetime import datetime
from pathlib import Path
from typing import ClassVar

from dagster import InitResourceContext
from pydicom import Dataset

from radis_etl_tkhd.resources import AditResource

PACS_AET = "TESTAET"
PACS_LINK_TEMPLATE = "http://pacs.test/viewer?acc={accession_number}"


class FakeAditResource(AditResource):
    """ADIT resource that serves canned studies and report instances instead of calling ADIT."""

    studies: ClassVar[list[Dataset]] = []
    instances: ClassVar[dict[str, Dataset]] = {}

    def setup_for_execution(self, context: InitResourceContext) -> None:
        assert context.log
        self._logger = context.log

    def fetch_studies_with_sr(self, ae_title: str, start: datetime, end: datetime) -> list[Dataset]:
        return list(self.studies)

    def fetch_report_dataset(self, ae_title: str, study_instance_uid: str) -> Dataset | None:
        return self.instances.get(study_instance_uid)


def make_study(study_uid: str) -> Dataset:
    study = Dataset()
    study.StudyInstanceUID = study_uid
    study.ModalitiesInStudy = ["CT", "SR"]
    return study


def make_report_instance(study_uid: str, accession_number: str, sop_uid: str, text: str) -> Dataset:
    instance = Dataset()
    instance.PatientID = "1005"
    instance.PatientBirthDate = "19760829"
    instance.PatientSex = "F"
    instance.StudyInstanceUID = study_uid
    instance.AccessionNumber = accession_number
    instance.StudyDescription = "CT Thorax"
    instance.StudyDate = "20240501"
    instance.StudyTime = "103000"
    instance.SeriesInstanceUID = f"{study_uid}.1"
    instance.SOPInstanceUID = sop_uid
    instance.TextValue = text
    return instance


def reports_file(artifacts_dir: Path, partition: str) -> Path:
    """The file the IO manager writes the reports of a partition to."""
    return artifacts_dir / f"reports-{partition}.json.gz"
