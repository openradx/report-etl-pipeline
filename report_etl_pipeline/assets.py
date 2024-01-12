import os
import re
from datetime import datetime, timedelta

from dagster import (
    AssetExecutionContext,
    Config,
    DailyPartitionsDefinition,
    asset,
)
from pydicom import Dataset

from .errors import FetchingError
from .models import RadisReport, Report, ReportWithReferences
from .resources import AditResource
from .utils import convert_to_python_date, convert_to_python_time, extract_report_text

partition_def = DailyPartitionsDefinition(start_date=datetime(2020, 1, 1))


class PacsConfig(Config):
    pacs_name: str = os.environ.get("PACS_NAME", "")
    pacs_ae_title: str = os.environ.get("PACS_AE_TITLE", "")


@asset(partitions_def=partition_def)
def reports_from_adit(
    context: AssetExecutionContext, config: PacsConfig, adit: AditResource
) -> list[Report]:
    context.log.info(f"Fetching reports from ADIT for partition {context.partition_key}.")

    time_window = context.partition_time_window
    start = time_window.start
    end = time_window.end - timedelta(seconds=1)

    studies = adit.fetch_studies_with_sr(config.pacs_ae_title, start, end)
    context.log.info(f"{len(studies)} studies found to extract reports from.")

    fetched_reports: list[Report] = []
    failed_studies: list[Dataset] = []
    for study in studies:
        try:
            instance = adit.fetch_report_dataset(config.pacs_ae_title, study.StudyInstanceUID)
        except Exception as err:
            context.log.error(f"Failed to fetch dataset of study {study.StudyInstanceUID}: {err}")
            failed_studies.append(study)
            continue

        if not instance:
            context.log.debug(f"No radiological report found in study {study.StudyInstanceUID}.")
            continue
        if not instance.get("AccessionNumber"):
            # External studies may not have an accession number. We skip those.
            context.log.debug(f"Missing accession number in study {study.StudyInstanceUID}.")
            continue

        # ModalitiesInStudy can be of type str or MultiValue and must be explicitly
        # converted to a list
        modalities_in_study = list(study.ModalitiesInStudy)

        body = extract_report_text(instance)
        if not body:
            context.log.warn(f"Missing report text in study {study.StudyInstanceUID}.")
            continue

        report = Report(
            pacs_aet=config.pacs_ae_title,
            pacs_name=config.pacs_name,
            patient_id=instance.PatientID,
            patient_birth_date=instance.PatientBirthDate,
            patient_sex=instance.PatientSex,
            study_instance_uid=instance.StudyInstanceUID,
            accession_number=instance.AccessionNumber,
            study_description=instance.StudyDescription,
            study_date=instance.StudyDate,
            study_time=instance.StudyTime,
            modalities_in_study=modalities_in_study,
            series_instance_uid=instance.SeriesInstanceUID,
            sop_instance_uid=instance.SOPInstanceUID,
            body=body,
        )
        fetched_reports.append(report)

    num_reports = len(fetched_reports)
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

    return fetched_reports


@asset(partitions_def=partition_def)
def reports_cleaned(
    context: AssetExecutionContext, reports_from_adit: list[Report]
) -> list[Report]:
    context.log.info("Cleanup fetched reports.")

    befunder_pattern = re.compile(r"Befunder:.*")
    newline_pattern = re.compile(r"<br>")
    reports = reports_from_adit
    for report in reports:
        body = report.body
        body = befunder_pattern.sub("", body)
        body = newline_pattern.sub("\n", body)
        body = body.strip()
        report.body = body

    context.log.info("Cleanup finished.")

    return reports


@asset(partitions_def=partition_def)
def reports_with_references(
    reports_cleaned: list[Report], adit: AditResource
) -> list[ReportWithReferences]:
    base_url = "http://thor-pacs02/Synapse/WebQuery/Index?path=/Alle%20Studien/accessionnumber="

    reports_with_references: list[ReportWithReferences] = []
    for report in reports_cleaned:
        references: list[str] = []
        if report.accession_number:
            references.append(base_url + report.accession_number)

        reports_with_references.append(
            ReportWithReferences.model_validate({**report.model_dump(), "references": references})
        )

    return reports_with_references


@asset(partitions_def=partition_def)
def radis_reports(reports_with_references: list[ReportWithReferences]) -> None:
    for report in reports_with_references:
        document_id = f"{report.pacs_aet}_{report.accession_number}"
        patient_birth_date = convert_to_python_date(report.patient_birth_date)
        study_date = convert_to_python_date(report.study_date)
        study_time = convert_to_python_time(report.study_time)
        study_datetime = datetime.combine(study_date, study_time)
        radis_report = RadisReport.model_validate(
            {
                **report.model_dump(),
                "document_id": document_id,
                "patient_birth_date": patient_birth_date.isoformat(),
                "study_datetime": study_datetime.isoformat(),
            }
        )
        # TODO: Store report in RADIS
