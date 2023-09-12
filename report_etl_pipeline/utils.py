import re

from pydicom import Dataset


def extract_report_text(ds: Dataset) -> str | None:
    if "TextValue" in ds:
        return ds.TextValue
    elif "ContentSequence" in ds:
        for seq in ds.ContentSequence:
            return extract_report_text(seq)

    return None


def filter_radiological_report_series(series_list: list[Dataset]) -> list[Dataset]:
    # Filter out radiological reports as there may be other SR series,
    # e.g. 'Radiation Dose Information'.
    p = re.compile("Radiological Report", re.IGNORECASE)
    return [series for series in series_list if p.search(series.SeriesDescription)]
