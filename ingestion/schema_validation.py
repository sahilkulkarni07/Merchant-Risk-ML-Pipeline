import pandas as pd


REQUIRED_COLUMNS = [
    "merchant_id",
    "name",
    "country",
    "registration_number",
    "monthly_volume",
    "dispute_count",
    "transaction_count",
]


def validate_schema(df: pd.DataFrame) -> None:
    """
    Validates merchant CSV schema and business rules.
    Raises ValueError if validation fails.
    """

    # Checking required columns
    
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # merchant_id validation
    
    if df["merchant_id"].isnull().any():
        raise ValueError("merchant_id contains null values")

    if not df["merchant_id"].str.startswith("M").all():
        raise ValueError("merchant_id must start with 'M'")

    if df["merchant_id"].duplicated().any():
        raise ValueError("Duplicate merchant_id found")

    # name validation
    
    if df["name"].isnull().any():
        raise ValueError("Merchant name contains null values")

    # country validation
    
    if df["country"].isnull().any():
        raise ValueError("Country contains null values")

    # Numeric fields validation
    
    numeric_fields = ["monthly_volume", "dispute_count", "transaction_count"]

    for field in numeric_fields:
        if not pd.api.types.is_numeric_dtype(df[field]):
            raise ValueError(f"{field} must be numeric")

        if (df[field] < 0).any():
            raise ValueError(f"{field} contains negative values")

    # transaction_count must be > 0
    
    if (df["transaction_count"] == 0).any():
        raise ValueError("transaction_count must be greater than 0")
