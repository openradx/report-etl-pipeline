import json

from dagster import (
    AssetExecutionContext,
    asset,
)

from ..models import AditReport, SanitizedReport
from ..partitions import collect_report_partitions_def
from ..resources import AditResource, RadisResource
from .common import (
    PacsConfig,
    SanitizeConfig,
    fetch_reports_from_adit,
    sanitize_report,
)


@asset(group_name="collected_reports", partitions_def=collect_report_partitions_def)
def adit_collected_reports(
    context: AssetExecutionContext, config: PacsConfig, adit: AditResource
) -> list[dict]:
    reports = fetch_reports_from_adit(context, config, adit)
    return [json.loads(report.model_dump_json()) for report in reports]


@asset(group_name="collected_reports", partitions_def=collect_report_partitions_def)
def sanitized_collected_reports(
    context: AssetExecutionContext, config: SanitizeConfig, adit_collected_reports: list[dict]
) -> list[dict]:
    reports = [
        AditReport.model_validate_json(json.dumps(report)) for report in adit_collected_reports
    ]

    context.log.info(f"Sanitize {len(reports)} reports.")

    sanitized_reports: list[SanitizedReport] = []
    for report in reports:
        sanitized_reports.append(sanitize_report(report, config))

    context.log.info("Sanitization finished.")

    return [json.loads(report.model_dump_json()) for report in sanitized_reports]


@asset(group_name="collected_reports", partitions_def=collect_report_partitions_def)
def radis_reports(
    context: AssetExecutionContext, sanitized_collected_reports: list[dict], radis: RadisResource
) -> None:
    reports = [
        SanitizedReport.model_validate_json(json.dumps(report))
        for report in sanitized_collected_reports
    ]

    context.log.info(f"Uploading {len(reports)} collected reports to RADIS.")

    for report in reports:
        radis.store_report(report)

    context.log.info("Upload finished.")
