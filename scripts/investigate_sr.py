import argparse
import os

from adit_client import AditClient
from dotenv import load_dotenv
from pydicom import Dataset

from report_etl_pipeline.utils import extract_report_text

load_dotenv(override=True)

pacs_ae_title = os.environ["PACS_AE_TITLE"]
adit_host = os.environ["ADIT_HOST"]
adit_auth_token = os.environ["ADIT_AUTH_TOKEN"]

parser = argparse.ArgumentParser()
parser.add_argument("study_instance_uid")

args = parser.parse_args()

study_instance_uid = args.study_instance_uid

client = AditClient(adit_host, adit_auth_token)

studies = client.search_for_studies(pacs_ae_title, {"StudyInstanceUID": study_instance_uid})

print(f"Studies (length {len(studies)}):")
print(studies)
print("--------------------------------")

series_list = client.search_for_series(pacs_ae_title, study_instance_uid, {"Modality": "SR"})

print(f"Series (length {len(series_list)}):")
print(series_list)
print("--------------------------------")

instances = client.retrieve_series(
    pacs_ae_title, study_instance_uid, series_list[0].SeriesInstanceUID
)

print("Radiological report:")
report_text = extract_report_text(instances[0])
print(report_text)
