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

Report = OriginalReport | SanitizedReport


class ReportIOManager(IOManager):
    def __init__(self, artifacts_dir: str):
        makedirs(artifacts_dir, exist_ok=True)
        self.artifacts_dir = artifacts_dir

    def handle_output(self, context: OutputContext, obj: list[Report]):
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

    def load_input(self, context: InputContext) -> list[Report]:
        assert context.metadata
        data_type = context.metadata["data_type"]
        if data_type == SanitizedReport.__name__:
            data_class = SanitizedReport
        elif data_type == OriginalReport.__name__:
            data_class = OriginalReport
        else:
            raise AssertionError(f"Unknown data type: {data_type}")

        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        filepath = Path(self.artifacts_dir) / f"reports-{context.asset_partition_key}.csv.gz"
        df: pd.DataFrame = pd.read_csv(filepath, compression="gzip", dtype=str)
        records = df.to_dict("records")

        reports: list[Report] = []
        for record in records:
            reports.append(data_class.from_record(record))

        context.log.info(f"Loaded {len(records)} records from {filepath}.")

        return reports


class ReportIOManagerFactory(ConfigurableIOManagerFactory):
    artifacts_dir: str | None = None

    def create_io_manager(self, context: InitResourceContext) -> ReportIOManager:
        if not context.instance:
            raise AssertionError("Missing instance in IO manager factory")

        artifacts_dir = self.artifacts_dir
        if not self.artifacts_dir:
            artifacts_dir = context.instance.storage_directory()

        artifacts_path = Path(artifacts_dir)
        if not artifacts_path.is_absolute():
            artifacts_path = Path(context.instance.root_directory) / artifacts_path

        artifacts_path.mkdir(parents=True, exist_ok=True)

        return ReportIOManager(artifacts_path.as_posix())
