from pathlib import Path

import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Amazon sales data for dashboard use.

    The function removes rows that cannot be converted into usable numeric values
    for the price, discount, rating, or rating count fields. Currency values are
    stripped of the ₹ symbol and commas, percentages are parsed as numeric values,
    and the rating column is coerced to numeric while preserving missing values.
    """
    cleaned = df.copy()

    for column in ["discounted_price", "actual_price"]:
        cleaned[column] = pd.to_numeric(
            cleaned[column].astype(str).str.replace(r"[^0-9.-]", "", regex=True),
            errors="coerce",
        )

    cleaned["discount_percentage"] = pd.to_numeric(
        cleaned["discount_percentage"].astype(str).str.replace(r"[^0-9.-]", "", regex=True),
        errors="coerce",
    )

    cleaned["rating"] = pd.to_numeric(cleaned["rating"], errors="coerce")

    cleaned["rating_count"] = pd.to_numeric(
        cleaned["rating_count"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    cleaned = cleaned.dropna(
        subset=["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"],
        how="any",
    ).reset_index(drop=True)

    return cleaned


data_path = Path(__file__).resolve().parent / "data" / "raw" / "amazon.csv"
raw_df = pd.read_csv(data_path)
cleaned_df = clean_data(raw_df)

before_rows = len(raw_df)
after_rows = len(cleaned_df)
dropped_rows = before_rows - after_rows

print(f"Rows before cleaning: {before_rows}")
print(f"Rows after cleaning: {after_rows}")
print(f"Rows dropped: {dropped_rows}")
print("\nPreview of first 5 cleaned rows:")
print(
    cleaned_df[["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]]
    .head(5)
    .to_string(index=False)
)

