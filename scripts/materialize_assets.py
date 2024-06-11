"""
This script is used to materialize the assets for a given partition date from the command line
and without using the Dagster Web UI.
"""

import argparse
import os
from pathlib import Path

from dagster import materialize
from dotenv import load_dotenv

from report_etl_pipeline.assets.collected_reports import (
    adit_collected_reports,
    sanitized_collected_reports,
)
from report_etl_pipeline.io_managers import ReportIOManager
from report_etl_pipeline.resources import AditResource

load_dotenv(override=True)

host = os.environ["ADIT_HOST"]
token = os.environ["ADIT_AUTH_TOKEN"]


def materialize_assets(partition: str, artifacts_dir: str):
    materialize(
        [adit_collected_reports, sanitized_collected_reports],
        partition_key=partition,
        resources={
            "adit": AditResource(host=host, auth_token=token, ca_bundle=""),
            "io_manager": ReportIOManager(artifacts_dir=artifacts_dir),
        },
        run_config={
            "ops": {
                "reports_from_adit": {
                    "config": {
                        "pacs_name": os.environ["PACS_NAME"],
                        "pacs_ae_title": os.environ["PACS_AE_TITLE"],
                    }
                }
            }
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("partition", help="The partition date to materialize, e.g. 2023-08-31")
    parser.add_argument("-d", "--dir", help="The directory to store the artifacts in", default="./")
    args = parser.parse_args()

    if not Path(args.dir).exists() or not Path(args.dir).is_dir():
        raise ValueError(f"Invalid directory to store artifacts: {args.dir}")
    artifacts_dir = Path(args.dir).absolute().as_posix()

    materialize_assets(args.partition, artifacts_dir)
