from pathlib import Path

import pandas as pd
from dagster import (
    ConfigurableIOManager,
    ConfigurableIOManagerFactory,
    InitResourceContext,
    InputContext,
    OutputContext,
)

from .types import Report


class ReportIOManager(ConfigurableIOManager):
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)

    def handle_output(self, context: OutputContext, obj: list[Report]):
        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        for report in obj:
            report["patient_birth_date"] = report["patient_birth_date"].isoformat()
            report["study_date"] = report["study_date"].isoformat()
            report["study_time"] = report["study_time"].isoformat()
            report["modalities_in_study"] = "|".join(report["modalities_in_study"])
            report["references"] = "|".join(report["references"])

        df = pd.DataFrame.from_records(obj)
        filepath = self.storage_dir / f"reports-{context.asset_partition_key}.csv.gz"
        df.to_csv(filepath, compression="gzip")

    def load_input(self, context: InputContext) -> list[Report]:
        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        filepath = self.storage_dir / f"reports-{context.asset_partition_key}.csv.gz"
        df = pd.read_csv(filepath, compression="gzip")
        data = df.to_dict("records")

        for item in data:
            item["patient_birth_date"] = pd.to_datetime(item["patient_birth_date"]).date()
            item["study_date"] = pd.to_datetime(item["study_date"]).date()
            item["study_time"] = pd.to_datetime(item["study_time"]).time()
            item["modalities_in_study"] = item["modalities_in_study"].split("|")
            item["references"] = item["references"].split("|")

        return data


class ReportIOManagerFactory(ConfigurableIOManagerFactory):
    def create_io_manager(self, context: InitResourceContext) -> ReportIOManager:
        storage_dir = context.instance.storage_directory()
        return ReportIOManager(storage_dir)
