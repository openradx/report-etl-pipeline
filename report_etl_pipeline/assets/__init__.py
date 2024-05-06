from dagster import load_assets_from_modules

from . import collected_reports, revised_reports

all_assets = load_assets_from_modules([collected_reports, revised_reports])
