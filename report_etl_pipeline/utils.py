import datetime
import re

from pydicom import Dataset, valuerep


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


def convert_to_python_date(value: str) -> datetime.date:
    """Convert a DICOM date string to a Python date object."""
    return datetime.date.fromisoformat(valuerep.DA(value).isoformat())


def convert_to_python_time(value: str) -> datetime.time:
    """Convert a DICOM date string to a Python date object."""
    return datetime.time.fromisoformat(valuerep.TM(value).isoformat())
