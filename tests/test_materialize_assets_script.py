"""Check of the command line script that materializes the collect assets for one partition."""

import gzip
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest
from helpers import PACS_AET, FakeAditResource, make_report_instance, make_study, reports_file

PARTITION = "2024-05-01"
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "materialize_assets.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("materialize_assets", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_materializes_collected_reports_for_partition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pipeline_env: None
) -> None:
    monkeypatch.setattr(FakeAditResource, "studies", [make_study("1.1")])
    monkeypatch.setattr(
        FakeAditResource,
        "instances",
        {"1.1": make_report_instance("1.1", "ACC1", "1.1.9", "Befund A<br>Befunder: X")},
    )
    adit = FakeAditResource(host="http://adit.test", auth_token="token", ca_bundle="")

    script = load_script()
    script.materialize_assets(PARTITION, tmp_path.as_posix(), adit)

    with gzip.open(reports_file(tmp_path, PARTITION)) as f:
        reports = json.load(f)
    assert [(r["document_id"], r["body_sanitized"]) for r in reports] == [
        (f"{PACS_AET}_ACC1", "Befund A")
    ]
