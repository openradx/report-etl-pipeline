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
    date_valuerep = valuerep.DA(value)
    assert date_valuerep is not None
    return datetime.date.fromisoformat(date_valuerep.isoformat())


def convert_to_python_time(value: str) -> datetime.time:
    """Convert a DICOM date string to a Python date object."""
    time_valuerep = valuerep.TM(value)
    assert time_valuerep is not None
    return datetime.time.fromisoformat(time_valuerep.isoformat())
