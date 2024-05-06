import json
from datetime import datetime, timezone

from dagster import (
    AssetExecutionContext,
    AssetKey,
    SourceAsset,
    asset,
)

from ..models import RevisedReport, SanitizedReport
from ..partitions import revised_report_partitions_def
from ..resources import AditResource, RadisResource
from .common import PacsSanitizeConfig, fetch_reports_from_adit, sanitize_report

collected_reports = SourceAsset(
    group_name="revised_reports",
    key=AssetKey("collected_reports"),
    partitions_def=revised_report_partitions_def,
)


@asset(group_name="revised_reports", partitions_def=revised_report_partitions_def)
def revised_reports(
    context: AssetExecutionContext,
    config: PacsSanitizeConfig,
    collected_reports: list[dict],
    adit: AditResource,
) -> list[dict]:
    old_reports = [
        SanitizedReport.model_validate_json(json.dumps(report)) for report in collected_reports
    ]
    new_reports = fetch_reports_from_adit(context, config, adit)

    # We need to sanitize the reports in this asset (and not in an own one) as we only want to
    # update existing data and only upload added and changed reports to RADIS.
    # Therefore we also keep unchanged reports in this asset and only mark the revised ones.

    revised_reports: list[RevisedReport] = []

    # Check for newly added reports
    for new_report in new_reports:
        if new_report.sop_instance_uid not in [report.sop_instance_uid for report in old_reports]:
            sanitized_report = sanitize_report(new_report, config)
            revised_reports.append(
                RevisedReport(
                    **sanitized_report.model_dump(),
                    revision_type="added",
                    revised_at=datetime.now(timezone.utc),
                )
            )

    # Check for changed reports
    for old_report in old_reports:
        changed = False
        for new_report in new_reports:
            if old_report.sop_instance_uid == new_report.sop_instance_uid:
                if old_report.body_original != new_report.body_original:
                    sanitized_report = sanitize_report(new_report, config)
                    revised_reports.append(
                        RevisedReport(
                            **sanitized_report.model_dump(),
                            revision_type="changed",
                            revised_at=datetime.now(timezone.utc),
                        )
                    )
                    changed = True

        # Add unchanged reports without a revision type
        if not changed:
            revised_reports.append(
                RevisedReport(
                    **old_report.model_dump(),
                    revision_type=None,
                    revised_at=None,
                )
            )

    # TODO: should we also handle deleted reports?!

    return [json.loads(report.model_dump_json()) for report in revised_reports]


@asset(group_name="revised_reports", partitions_def=revised_report_partitions_def)
def radis_revised_reports(
    context: AssetExecutionContext,
    revised_reports: list[dict],
    radis: RadisResource,
) -> None:
    reports = [RevisedReport.model_validate_json(json.dumps(report)) for report in revised_reports]

    # Filter out only the revised reports
    reports = [report for report in reports if report.revision_type is not None]

    context.log.info(f"Uploading {len(reports)} revised reports to RADIS.")

    for report in reports:
        radis.store_report(report)

    context.log.info("Upload finished.")
