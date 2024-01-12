from datetime import datetime, timedelta

from adit_client import AditClient
from dagster import ConfigurableResource, DagsterLogManager
from dagster._core.execution.context.init import InitResourceContext
from pydantic import Field, PrivateAttr
from pydicom import Dataset

from report_etl_pipeline.utils import filter_radiological_report_series

from .models import RadisReport


class AditResource(ConfigurableResource):
    host: str
    auth_token: str
    max_search_results: int = Field(
        default=199,
        description=(
            "The maximum number of SR series to query. Each PACS has a maximum result count. "
            "If the number of results is higher than this number will be automatically split "
            "during search."
        ),
    )

    _client: AditClient = PrivateAttr()
    _logger: DagsterLogManager = PrivateAttr()

    def setup_for_execution(self, context: InitResourceContext) -> None:
        self._client = AditClient(server_url=self.host, auth_token=self.auth_token)

        if not context.log:
            raise ValueError("Missing log manager.")

        self._logger = context.log

        return super().setup_for_execution(context)

    def fetch_studies_with_sr(self, ae_title: str, start: datetime, end: datetime) -> list[Dataset]:
        start_date = start.strftime("%Y%m%d")
        end_date = end.strftime("%Y%m%d")
        start_time = start.strftime("%H%M%S")
        end_time = end.strftime("%H%M%S")

        study_date = f"{start_date} - {end_date}" if start_date != end_date else start_date
        study_time = f"{start_time} - {end_time}" if start_time != end_time else start_time

        query = {
            "StudyDate": study_date,
            "StudyTime": study_time,
            "ModalitiesInStudy": "SR",
        }

        self._logger.debug(f"Search for studies: {query}")

        results = self._client.search_for_studies(ae_title, query)
        num_results = len(results)

        self._logger.debug(f"Number of found studies: {num_results}")

        if num_results > self.max_search_results:
            self._logger.debug("Too many studies found, narrowing time window.")
            delta = end - start

            if delta < timedelta(seconds=1800):  # 30 mins
                raise ValueError(f"Time window too small ({start} to {end}).")

            mid = start + delta / 2
            part1 = self.fetch_studies_with_sr(ae_title, start, mid)
            part2 = self.fetch_studies_with_sr(ae_title, mid, end)
            return part1 + part2

        return results

    def fetch_report_dataset(self, ae_title: str, study_instance_uid: str) -> Dataset | None:
        self._logger.debug(f"Processing study {study_instance_uid}.")

        series_list = self._client.search_for_series(
            ae_title, study_instance_uid, {"Modality": "SR"}
        )
        series_list = filter_radiological_report_series(series_list)

        if len(series_list) == 0:
            return None
        if len(series_list) > 1:
            self._logger.warn(
                f"Multiple radiological report series in study {study_instance_uid}."
                "Only the first one will be used."
            )

        series = series_list[0]
        instances = self._client.retrieve_series(
            ae_title, series.StudyInstanceUID, series.SeriesInstanceUID
        )

        if len(instances) == 0:
            raise AssertionError(f"Missing report instance in study {study_instance_uid}.")
        if len(instances) > 1:
            self._logger.warn(
                f"Multiple radiological report instances in study {study_instance_uid}. "
                "Only the first one will be used."
            )

        return instances[0]


class RadisResource(ConfigurableResource):
    radis_host: str
    auth_token: str

    # TODO: Implement this stuff
    # _client: RadisClient = PrivateAttr()

    def store_report(self, report: RadisReport) -> None:
        pass
