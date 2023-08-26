from datetime import datetime

from adit_client import AditClient
from dagster import ConfigurableResource, TimeWindow
from dagster._core.execution.context.init import InitResourceContext
from pydantic import Field, PrivateAttr
from pydicom import Dataset

from .types import RadisReport


class AditResource(ConfigurableResource):
    adit_host: str
    auth_token: str
    max_search_results: int = Field(
        default=100,
        description=(
            "The maximum number of SR series to query. Each PACS has a maximum result count. "
            "If the number of results is higher than this number we must split the search."
        ),
    )

    _client: AditClient = PrivateAttr()

    def setup_for_execution(self, context: InitResourceContext) -> None:
        self._client = AditClient(server_url=self.adit_host, auth_token=self.auth_token)
        return super().setup_for_execution(context)

    def fetch_structured_reports(self, ae_title: str, time_window: TimeWindow) -> list[Dataset]:
        def _fetch_datasets(start: datetime, end: datetime) -> list[Dataset]:
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")
            start_time = start.strftime("%H:%M:%S")
            end_time = end.strftime("%H:%M:%S")

            results = self._client.search_for_studies(
                ae_title,
                {
                    "StudyDate": f"{start_date} - {end_date}",
                    "StudyTime": f"{start_time} - {end_time}",
                    "ModalitiesInStudy": "SR",
                },
            )

            if len(results) > self.max_search_results:
                mid = start + (end - start) / 2
                return _fetch_datasets(start, mid) + _fetch_datasets(mid, end)

            return results

        return _fetch_datasets(time_window.start, time_window.end)

    def fetch_reference_images(self, study_instance_uid: str, max_count: int) -> list[Dataset]:
        # TODO: Fetch representative images for a study
        results: list[Dataset] = []
        return results


class RadisResource(ConfigurableResource):
    radis_host: str
    auth_token: str

    # TODO: Implement this stuff
    # _client: RadisClient = PrivateAttr()

    def store_report(self, report: RadisReport) -> None:
        pass
