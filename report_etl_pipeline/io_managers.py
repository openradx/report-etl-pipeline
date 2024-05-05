import gzip
import json
from os import makedirs
from pathlib import Path

from dagster import (
    ConfigurableIOManagerFactory,
    InitResourceContext,
    InputContext,
    IOManager,
    OutputContext,
)


class ReportIOManager(IOManager):
    def __init__(self, artifacts_dir: str):
        makedirs(artifacts_dir, exist_ok=True)
        self.artifacts_dir = artifacts_dir

    def handle_output(self, context: OutputContext, obj: list[dict]):
        if obj is None:
            return

        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        filepath = Path(self.artifacts_dir) / f"reports-{context.asset_partition_key}.json.gz"

        json_str = json.dumps(obj)
        json_bytes = json_str.encode("utf-8")

        with gzip.open(filepath, "w") as fout:
            fout.write(json_bytes)

        context.log.info(f"Saved {len(obj)} to {filepath}.")

    def load_input(self, context: InputContext) -> list[dict]:
        if not context.asset_partition_key:
            raise AssertionError("Missing partition key in IO manager")

        filepath = Path(self.artifacts_dir) / f"reports-{context.asset_partition_key}.json.gz"

        with gzip.open(filepath, "r") as fin:
            json_bytes = fin.read()

        json_str = json_bytes.decode("utf-8")
        records = json.loads(json_str)

        context.log.info(f"Loaded {len(records)} records from {filepath}.")

        return records


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
