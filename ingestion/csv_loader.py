import pandas as pd
from ingestion.schema_validation import validate_schema


def load_merchants_csv(file_path: str) -> pd.DataFrame:
    """
    Loads merchants CSV and validates schema.
    """

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    validate_schema(df)

    return df