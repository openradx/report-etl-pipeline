"""Checks of the top-level definitions that depend on the deployment environment."""

import importlib
from collections.abc import Iterator

import pytest
from dagster import DefaultScheduleStatus, Definitions

import radis_etl_tkhd

SCHEDULES = ["collect_reports_job_schedule", "revise_reports_job_schedule"]


def load_definitions(monkeypatch: pytest.MonkeyPatch, deployment: str | None) -> Definitions:
    """Reload the package so that its module-level definitions see the given deployment."""
    if deployment is None:
        monkeypatch.delenv("DAGSTER_DEPLOYMENT", raising=False)
    else:
        monkeypatch.setenv("DAGSTER_DEPLOYMENT", deployment)
    return importlib.reload(radis_etl_tkhd).defs


@pytest.fixture(autouse=True)
def restore_definitions() -> Iterator[None]:
    """Reload the package again after the environment has been restored by monkeypatch."""
    yield
    importlib.reload(radis_etl_tkhd)


@pytest.mark.parametrize("deployment", [None, "dev"])
def test_schedules_stay_stopped_outside_production(
    monkeypatch: pytest.MonkeyPatch, deployment: str | None
) -> None:
    defs = load_definitions(monkeypatch, deployment)
    for name in SCHEDULES:
        assert defs.resolve_schedule_def(name).default_status == DefaultScheduleStatus.STOPPED


def test_schedules_start_running_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    defs = load_definitions(monkeypatch, "prod")
    for name in SCHEDULES:
        assert defs.resolve_schedule_def(name).default_status == DefaultScheduleStatus.RUNNING
