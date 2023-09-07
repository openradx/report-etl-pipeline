import argparse
import os
from pathlib import Path

from dagster import materialize
from dotenv import load_dotenv

from report_etl_pipeline.assets import reports_cleaned, reports_from_adit, reports_with_references
from report_etl_pipeline.io_managers import ReportIOManager
from report_etl_pipeline.resources import AditResource

load_dotenv(override=True)

PROJECT_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = PROJECT_DIR / "env" / "artifacts"

host = os.environ["ADIT_HOST"]
token = os.environ["ADIT_AUTH_TOKEN"]


def materialize_assets(partition: str):
    materialize(
        [reports_from_adit, reports_cleaned, reports_with_references],
        partition_key=partition,
        resources={
            "adit": AditResource(host=host, auth_token=token),
            "io_manager": ReportIOManager(base_dir=ARTIFACTS_DIR.as_posix()),
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
    args = parser.parse_args()

    materialize_assets(args.partition)
