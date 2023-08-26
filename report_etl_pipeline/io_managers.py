from pathlib import Path
from typing import Any

import pandas as pd
from dagster import (
    ConfigurableIOManager,
    ConfigurableIOManagerFactory,
    InitResourceContext,
    InputContext,
    OutputContext,
)

from .types import Report, ReportWithReferences


class ReportIOManager(ConfigurableIOManager):
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)

    def handle_output(self, context: OutputContext, obj: list[Report | ReportWithReferences]):
        if obj is None:
            return

        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        records: list[dict[str, Any]] = []
        for report in obj:
            record: dict[str, Any] = {}
            record.update(report)
            record["modalities_in_study"] = "|".join(report["modalities_in_study"])

            if isinstance(report, ReportWithReferences):
                record["references"] = "|".join(report["references"])

        df = pd.DataFrame.from_records(records)
        filepath = self.storage_dir / f"reports-{context.asset_partition_key}.csv.gz"
        df.to_csv(filepath, compression="gzip")

    def load_input(self, context: InputContext) -> list[Report | ReportWithReferences]:
        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        filepath = self.storage_dir / f"reports-{context.asset_partition_key}.csv.gz"
        df: pd.DataFrame = pd.read_csv(filepath, compression="gzip")
        records = df.to_dict("records")

        for record in records:
            record["modalities_in_study"] = record["modalities_in_study"].split("|")

            if "references" in record:
                record["references"] = record["references"].split("|")

        return records  # type: ignore


class ReportIOManagerFactory(ConfigurableIOManagerFactory):
    def create_io_manager(self, context: InitResourceContext) -> ReportIOManager:
        if not context.instance:
            raise AssertionError("Missing instance in IO manager factory")

        storage_dir = context.instance.storage_directory()
        return ReportIOManager(storage_dir)
