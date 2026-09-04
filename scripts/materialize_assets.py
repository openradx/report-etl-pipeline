"""
Materialize the collect assets (fetch the reports from ADIT and sanitize them) for a given
partition date from the command line and without the Dagster web UI. The reports are written
to the given directory, but not uploaded to RADIS.

The ADIT, PACS and sanitize settings are read from the environment (or a `.env` file), just
like in the Dagster deployment.
"""

import argparse
import os
from pathlib import Path

from dagster import materialize
from dotenv import load_dotenv

from radis_etl_tkhd.assets.collected_reports import (
    adit_collected_reports,
    sanitized_collected_reports,
)
from radis_etl_tkhd.io_managers import ReportIOManagerFactory
from radis_etl_tkhd.resources import AditResource


def materialize_assets(partition: str, artifacts_dir: str, adit: AditResource) -> None:
    materialize(
        [adit_collected_reports, sanitized_collected_reports],
        partition_key=partition,
        resources={
            "adit": adit,
            "io_manager": ReportIOManagerFactory(artifacts_dir=artifacts_dir),
        },
    )


def main() -> None:
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("partition", help="The partition date to materialize, e.g. 2023-08-31")
    parser.add_argument("-d", "--dir", help="The directory to store the artifacts in", default="./")
    args = parser.parse_args()

    artifacts_dir = Path(args.dir)
    if not artifacts_dir.is_dir():
        raise ValueError(f"Invalid directory to store artifacts: {args.dir}")

    # The script runs against a temporary Dagster instance, so paths must be absolute here.
    ca_bundle = os.environ.get("CA_BUNDLE", "")
    if ca_bundle:
        ca_bundle = Path(ca_bundle).resolve().as_posix()

    adit = AditResource(
        host=os.environ["ADIT_HOST"],
        auth_token=os.environ["ADIT_AUTH_TOKEN"],
        ca_bundle=ca_bundle,
    )
    materialize_assets(args.partition, artifacts_dir.resolve().as_posix(), adit)


if __name__ == "__main__":
    main()
