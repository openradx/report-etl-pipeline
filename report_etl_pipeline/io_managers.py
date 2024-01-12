from os import makedirs
from pathlib import Path
from typing import Any

import pandas as pd
from dagster import (
    ConfigurableIOManagerFactory,
    InitResourceContext,
    InputContext,
    IOManager,
    OutputContext,
)

from .models import Report, ReportWithReferences


class ReportIOManager(IOManager):
    def __init__(self, artifacts_dir: str):
        makedirs(artifacts_dir, exist_ok=True)
        self.artifacts_dir = artifacts_dir

    def handle_output(self, context: OutputContext, obj: list[Report | ReportWithReferences]):
        if obj is None:
            return

        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        records: list[dict[str, Any]] = []
        for report in obj:
            record: dict[str, Any] = {}
            record.update(report.dict())
            record["modalities_in_study"] = "|".join(report.modalities_in_study)

            if isinstance(report, ReportWithReferences):
                record["references"] = "|".join(report.references)

            records.append(record)

        df = pd.DataFrame.from_records(records)
        filepath = Path(self.artifacts_dir) / f"reports-{context.asset_partition_key}.csv.gz"
        df.to_csv(filepath, compression="gzip")

        context.log.info(f"Saved {len(records)} to {filepath}.")

    def load_input(self, context: InputContext) -> list[Report] | list[ReportWithReferences]:
        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        filepath = Path(self.artifacts_dir) / f"reports-{context.asset_partition_key}.csv.gz"
        df: pd.DataFrame = pd.read_csv(filepath, compression="gzip", dtype=str)
        records = df.to_dict("records")

        reports: list[Report] | list[ReportWithReferences] = []
        for record in records:
            record["modalities_in_study"] = record["modalities_in_study"].split("|")
            if "references" in record:
                record["references"] = record["references"].split("|")
                reports.append(ReportWithReferences.model_validate(record))
            else:
                reports.append(Report.model_validate(record))

        context.log.info(f"Loaded {len(records)} records from {filepath}.")

        return reports


class ReportIOManagerFactory(ConfigurableIOManagerFactory):
    artifacts_dir: str | None = None

    def create_io_manager(self, context: InitResourceContext) -> ReportIOManager:
        if not context.instance:
            raise AssertionError("Missing instance in IO manager factory")

        if self.artifacts_dir is not None:
            artifacts_dir = Path(self.artifacts_dir).absolute().as_posix()
        else:
            artifacts_dir = context.instance.storage_directory()
        Path(artifacts_dir).mkdir(parents=True, exist_ok=True)

        return ReportIOManager(artifacts_dir)
