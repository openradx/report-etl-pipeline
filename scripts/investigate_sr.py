import argparse
import os

from adit_client import AditClient
from dotenv import load_dotenv

from report_etl_pipeline.utils import extract_report_text, filter_radiological_report_series

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

if len(studies) == 0:
    raise ValueError("No study found with this Study Instance UID")
if len(studies) > 1:
    raise ValueError("Multiple studies found with this Study Instance UID")

print("Study:")
print(studies[0])
print("==========")

series_list = client.search_for_series(pacs_ae_title, study_instance_uid, {"Modality": "SR"})
series_list = filter_radiological_report_series(series_list)

if len(series_list) == 0:
    raise ValueError("Missing SR series in this study.")
# if len(series_list) > 1:
#     raise ValueError("Multiple radiological report series in this study")

all_instances = []
for series in series_list:
    print("Series:")
    print(series)

    instances = client.retrieve_series(pacs_ae_title, study_instance_uid, series.SeriesInstanceUID)
    all_instances = all_instances + instances

    if len(instances) == 0:
        raise ValueError("Missing radiological report instance")
    # if len(instances) > 1:
    #     raise ValueError("Multiple radiological report instances")

    for instance in instances:
        print("\nInstance:")
        print(instance)

        print("\nReport:")
        report_text = extract_report_text(instances[0])
        print(report_text)

    print("----------")

print("Summary:")
print(f"Found {len(all_instances)} report instances in {len(series_list)} series.")
