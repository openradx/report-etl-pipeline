from datetime import date

from dagster import ConfigurableResource
from pydantic import Field
from pydicom import Dataset


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

    def fetch_sr_from_synapse(date: date) -> list[Dataset]:
        results: list[Dataset] = []
        return results
