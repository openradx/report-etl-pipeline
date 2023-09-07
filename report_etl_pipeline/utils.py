from pydicom import Dataset


def extract_report_text(ds: Dataset) -> str | None:
    if "TextValue" in ds:
        return ds.TextValue
    elif "ContentSequence" in ds:
        for seq in ds.ContentSequence:
            return extract_report_text(seq)

    return None
