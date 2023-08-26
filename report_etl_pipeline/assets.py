import os
from datetime import datetime

from dagster import (
    AssetExecutionContext,
    Config,
    DailyPartitionsDefinition,
    asset,
)

from .resources import AditResource
from .types import Report, ReportWithReferences

partition_def = DailyPartitionsDefinition(start_date=datetime(2020, 1, 1))


class SynapseConfig(Config):
    name: str = os.environ["SYNAPSE_NAME"]
    ae_title: str = os.environ["SYNAPSE_AE_TITLE"]


@asset(partitions_def=partition_def)
def reports_from_synapse(
    context: AssetExecutionContext, config: SynapseConfig, adit: AditResource
) -> list[Report]:
    datasets = adit.fetch_structured_reports(config.ae_title, context.partition_time_window)

    reports: list[Report] = []
    for ds in datasets:
        modalities_in_study = ds.ModalitiesInStudy
        if isinstance(modalities_in_study, str):
            modalities_in_study = [modalities_in_study]

        body = ds.ContentSequence[0].TextValue or ""
        body = body.strip()

        if not body:
            continue

        reports.append(
            {
                "pacs_aet": config.ae_title,
                "pacs_name": config.name,
                "patient_id": ds.PatientID,
                "patient_birth_date": ds.PatientBirthDate,
                "patient_sex": ds.PatientSex,
                "study_instance_uid": ds.StudyInstanceUID,
                "accession_number": ds.AccessionNumber,
                "study_description": ds.StudyDescription,
                "study_date": ds.StudyDate,
                "study_time": ds.StudyTime,
                "modalities_in_study": modalities_in_study,
                "series_instance_uid": ds.SeriesInstanceUID,
                "sop_instance_uid": ds.SOPInstanceUID,
                "body": body,
            }
        )

    context.add_output_metadata(
        metadata={
            "num_reports": len(reports),
        }
    )

    return reports


@asset(partitions_def=partition_def)
def reports_with_synapse_references(
    reports_from_synapse: list[Report], adit: AditResource
) -> list[ReportWithReferences]:
    report_with_references: list[ReportWithReferences] = []
    for report in reports_from_synapse:
        images = adit.fetch_reference_images(report["study_instance_uid"], 10)
        # TODO: Extract reference URL from images and put into report
        report_with_reference: ReportWithReferences = {**report, "references": []}
        report_with_references.append(report_with_reference)

    return report_with_references


@asset(partitions_def=partition_def)
def radis_reports(reports_with_synapse_references: list[Report]) -> None:
    pass
