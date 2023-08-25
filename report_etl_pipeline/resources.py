from adit_client import AditClient
from dagster import ConfigurableResource, TimeWindow
from dagster._core.execution.context.init import InitResourceContext
from pydantic import Field, PrivateAttr
from pydicom import Dataset


class AditResource(ConfigurableResource):
    adit_host: str
    auth_token: str
    ae_title: str
    max_search_results: int = Field(
        default=100,
        description=(
            "The maximum number of SR series to query. Each PACS has a maximum result count. "
            "If the number of results is higher than this number we must split the search."
        ),
    )

    _client: AditClient = PrivateAttr()

    def setup_for_execution(self, context: InitResourceContext) -> None:
        self._client = AditClient(host=self.adit_host, auth_token=self.auth_token)
        return super().setup_for_execution(context)

    def fetch_sr_from_synapse(self, time_window: TimeWindow) -> list[Dataset]:
        start = time_window.start.isoformat()
        end = time_window.end.isoformat()

        startDate = f"{start[:4]}-{start[4:6]}-{start[6:8]}"

        # TODO: correct date and time format
        search_results = self._client.search_for_studies(
            self.ae_title,
            {
                "StudyDate": f"{start} - {end}",
                "StudyTime": "000000-235959",
                "ModalitiesInStudy": "SR",
            },
        )
        if len(search_results) > self.max_search_results:
            # TODO: split search
            pass
        results: list[Dataset] = []
        return results
