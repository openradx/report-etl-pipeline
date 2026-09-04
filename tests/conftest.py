import pytest
from helpers import PACS_AET, PACS_LINK_TEMPLATE


@pytest.fixture
def pipeline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """The environment variables the asset configs read their defaults from."""
    monkeypatch.setenv("PACS_NAME", "Test PACS")
    monkeypatch.setenv("PACS_AE_TITLE", PACS_AET)
    monkeypatch.setenv("REPORT_LANGUAGE", "de")
    monkeypatch.setenv("GROUP_ID", "1")
    monkeypatch.setenv("PACS_LINK_TEMPLATE", PACS_LINK_TEMPLATE)
