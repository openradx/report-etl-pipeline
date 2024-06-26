import re
from datetime import datetime, timedelta, timezone

from dagster import (
    AssetExecutionContext,
    Config,
    EnvVar,
)
from pydantic import Field
from pydicom import Dataset

from ..errors import FetchingError
from ..models import AditReport, SanitizedReport
from ..resources import AditResource
from ..utils import convert_to_python_date, convert_to_python_time, extract_report_text


class PacsConfig(Config):
    pacs_name: str = Field(
        default=EnvVar("PACS_NAME"),
        description=(
            "The name of the PACS to query for reports (also stored in the report metadata)."
        ),
    )
    pacs_ae_title: str = Field(
        default=EnvVar("PACS_AE_TITLE"),
        description=(
            "The AE title of the PACS to query for reports (also stored in the report metadata)."
        ),
    )


class SanitizeConfig(Config):
    language: str = Field(
        default=EnvVar("REPORT_LANGUAGE"),
        description="The language of the reports.",
    )
    group: int = Field(
        default=EnvVar("GROUP_ID"),
        description="The group ID to assign to the reports.",
    )


class PacsSanitizeConfig(PacsConfig, SanitizeConfig):
    pass


def fetch_reports_from_adit(
    context: AssetExecutionContext, config: PacsConfig, adit: AditResource
) -> list[AditReport]:
    context.log.info(f"Fetching reports from ADIT for partition {context.partition_key}.")

    time_window = context.partition_time_window
    start = time_window.start
    end = time_window.end - timedelta(seconds=1)

    studies = adit.fetch_studies_with_sr(config.pacs_ae_title, start, end)
    context.log.info(f"{len(studies)} studies with SR modality found.")

    reports: list[AditReport] = []
    failed_studies: list[Dataset] = []
    for study in studies:
        try:
            instance = adit.fetch_report_dataset(config.pacs_ae_title, study.StudyInstanceUID)
        except Exception as err:
            context.log.error(
                f"Failed to fetch SR instance of study {study.StudyInstanceUID}: {err}"
            )
            failed_studies.append(study)
            continue

        if not instance:
            context.log.debug(f"No SR instance found in study {study.StudyInstanceUID}.")
            continue
        if not instance.get("AccessionNumber"):
            # External studies may not have an accession number. We skip those as we need it
            # to generate a unique document ID.
            context.log.debug(f"Missing accession number in study {study.StudyInstanceUID}.")
            continue

        # ModalitiesInStudy can be of type str or MultiValue and must be explicitly
        # converted to a list
        modalities_in_study = list(study.ModalitiesInStudy)

        body_original = extract_report_text(instance)
        if not body_original:
            context.log.warn(f"Missing report text in study {study.StudyInstanceUID}.")
            continue

        patient_birth_date = convert_to_python_date(instance.PatientBirthDate)

        study_date = convert_to_python_date(instance.StudyDate)
        study_time = convert_to_python_time(instance.StudyTime)
        study_datetime = datetime.combine(study_date, study_time)

        reports.append(
            AditReport(
                pacs_aet=config.pacs_ae_title,
                pacs_name=config.pacs_name,
                patient_id=instance.PatientID,
                patient_birth_date=patient_birth_date,
                patient_sex=instance.PatientSex,
                study_instance_uid=instance.StudyInstanceUID,
                accession_number=instance.AccessionNumber,
                study_description=instance.StudyDescription,
                study_datetime=study_datetime,
                modalities_in_study=modalities_in_study,
                series_instance_uid=instance.SeriesInstanceUID,
                sop_instance_uid=instance.SOPInstanceUID,
                body_original=body_original,
                created_at=datetime.now(timezone.utc),
            )
        )

    num_reports = len(reports)
    num_failed = len(failed_studies)

    if num_reports == 0 and len(failed_studies) > 0:
        raise FetchingError(f"All report fetches failed for partition {context.partition_key}.")

    if num_failed > 0:
        studies_label = "studies" if num_failed > 1 else "study"
        context.log.error(f"Failed to fetch instances of {num_failed} {studies_label}.")

    context.log.info(f"Found {num_reports} reports for partition {context.partition_key}.")
    context.add_output_metadata(
        metadata={
            "num_reports": num_reports,
            "num_failed": num_failed,
        }
    )

    return reports


def create_document_id(report: AditReport):
    return f"{report.pacs_aet}_{report.accession_number}"


def sanitize_report(report: AditReport, config: SanitizeConfig) -> SanitizedReport:
    befunder_pattern = re.compile(r"Befunder:.*")
    newline_pattern = re.compile(r"<br>")

    link_base_url = (
        "http://thor-pacs02/Synapse/WebQuery/Index?path=/Alle%20Studien/accessionnumber="
    )

    document_id = f"{report.pacs_aet}_{report.accession_number}"

    # Sanitize the report body
    body_sanitized = report.body_original
    body_sanitized = befunder_pattern.sub("", body_sanitized)
    body_sanitized = newline_pattern.sub("\n", body_sanitized)
    body_sanitized = body_sanitized.strip()

    return SanitizedReport(
        **report.model_dump(),
        document_id=document_id,
        language=config.language,
        groups=[config.group],
        pacs_link=link_base_url + report.accession_number,
        body_sanitized=body_sanitized,
    )
