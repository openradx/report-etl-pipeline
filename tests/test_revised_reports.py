"""End-to-end check of the revise reports flow without external services.

Materializes the `revised_reports` asset for one partition with a fake ADIT resource and a
pre-seeded artifacts directory. This verifies that the external `collected_reports` asset is
loaded through the IO manager, that reports are fetched, sanitized and compared with the
previously collected ones, and that the result is written back to the artifacts directory.
"""

import gzip
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import ClassVar

import pytest
from dagster import InitResourceContext, materialize
from pydicom import Dataset

from radis_etl_tkhd.assets.revised_reports import collected_reports, revised_reports
from radis_etl_tkhd.io_managers import ReportIOManagerFactory
from radis_etl_tkhd.models import SanitizedReport
from radis_etl_tkhd.resources import AditResource

PARTITION = "2024-05-01"
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


def make_collected_report(
    study_uid: str, accession_number: str, sop_uid: str, body: str
) -> SanitizedReport:
    return SanitizedReport(
        pacs_aet=PACS_AET,
        pacs_name="Test PACS",
        patient_id="1005",
        patient_birth_date=date(1976, 8, 29),
        patient_sex="F",
        study_instance_uid=study_uid,
        accession_number=accession_number,
        study_description="CT Thorax",
        study_datetime=datetime(2024, 5, 1, 10, 30),
        modalities_in_study=["CT", "SR"],
        series_instance_uid=f"{study_uid}.1",
        sop_instance_uid=sop_uid,
        body_original=body,
        created_at=datetime.now(timezone.utc),
        document_id=f"{PACS_AET}_{accession_number}",
        language="de",
        groups=[1],
        pacs_link=PACS_LINK_TEMPLATE.format(accession_number=accession_number),
        body_sanitized=body,
    )


def reports_file(artifacts_dir: Path) -> Path:
    return artifacts_dir / f"reports-{PARTITION}.json.gz"


@pytest.fixture
def pipeline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PACS_NAME", "Test PACS")
    monkeypatch.setenv("PACS_AE_TITLE", PACS_AET)
    monkeypatch.setenv("REPORT_LANGUAGE", "de")
    monkeypatch.setenv("GROUP_ID", "1")
    monkeypatch.setenv("PACS_LINK_TEMPLATE", PACS_LINK_TEMPLATE)


def test_revised_reports_detects_unchanged_changed_and_added_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pipeline_env: None
) -> None:
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    # Reports collected earlier: study 1 is unchanged since, study 2 was revised.
    collected = [
        make_collected_report("1.1", "ACC1", "1.1.9", "Befund A"),
        make_collected_report("1.2", "ACC2", "1.2.9", "Befund B (old)"),
    ]
    with gzip.open(reports_file(artifacts_dir), "w") as f:
        f.write(json.dumps([json.loads(r.model_dump_json()) for r in collected]).encode())

    # Reports in the PACS now: study 1 unchanged, study 2 changed, study 3 added.
    monkeypatch.setattr(
        FakeAditResource, "studies", [make_study("1.1"), make_study("1.2"), make_study("1.3")]
    )
    monkeypatch.setattr(
        FakeAditResource,
        "instances",
        {
            "1.1": make_report_instance("1.1", "ACC1", "1.1.9", "Befund A"),
            "1.2": make_report_instance("1.2", "ACC2", "1.2.9", "Befund B (new)<br>Befunder: X"),
            "1.3": make_report_instance("1.3", "ACC3", "1.3.9", "Befund C"),
        },
    )

    result = materialize(
        [collected_reports, revised_reports],
        partition_key=PARTITION,
        resources={
            "io_manager": ReportIOManagerFactory(artifacts_dir=artifacts_dir.as_posix()),
            "adit": FakeAditResource(host="http://adit.test", auth_token="token", ca_bundle=""),
        },
    )
    assert result.success

    output = {r["sop_instance_uid"]: r for r in result.output_for_node("revised_reports")}
    assert {sop: r["revision_type"] for sop, r in output.items()} == {
        "1.1.9": None,
        "1.2.9": "changed",
        "1.3.9": "added",
    }

    changed = output["1.2.9"]
    assert changed["body_original"] == "Befund B (new)<br>Befunder: X"
    assert changed["body_sanitized"] == "Befund B (new)"
    assert changed["document_id"] == f"{PACS_AET}_ACC2"
    assert changed["pacs_link"] == "http://pacs.test/viewer?acc=ACC2"
    assert changed["study_datetime"] == "2024-05-01T10:30:00"

    metadata = result.asset_materializations_for_node("revised_reports")[0].metadata
    assert metadata["num_reports_unchanged"].value == 1
    assert metadata["num_reports_changed"].value == 1
    assert metadata["num_reports_added"].value == 1

    # The revised reports replace the previously collected ones in the artifacts directory.
    with gzip.open(reports_file(artifacts_dir)) as f:
        assert len(json.load(f)) == 3
