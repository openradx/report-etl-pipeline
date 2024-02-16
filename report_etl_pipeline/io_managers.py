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

from .models import OriginalReport, SanitizedReport


class ReportIOManager(IOManager):
    def __init__(self, artifacts_dir: str):
        makedirs(artifacts_dir, exist_ok=True)
        self.artifacts_dir = artifacts_dir

    def handle_output(self, context: OutputContext, obj: list[OriginalReport | SanitizedReport]):
        if obj is None:
            return

        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        records: list[dict[str, Any]] = []
        for report in obj:
            records.append(report.to_record())

        df = pd.DataFrame.from_records(records)
        filepath = Path(self.artifacts_dir) / f"reports-{context.asset_partition_key}.csv.gz"
        df.to_csv(filepath, compression="gzip")

        context.log.info(f"Saved {len(records)} to {filepath}.")

    def load_input(self, context: InputContext) -> list[OriginalReport] | list[SanitizedReport]:
        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        filepath = Path(self.artifacts_dir) / f"reports-{context.asset_partition_key}.csv.gz"
        df: pd.DataFrame = pd.read_csv(filepath, compression="gzip", dtype=str)
        records = df.to_dict("records")

        reports: list[OriginalReport] | list[SanitizedReport] = []
        for record in records:
            if "document_id" in record:
                reports.append(SanitizedReport.from_record(record))
            else:
                reports.append(OriginalReport.from_record(record))

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
