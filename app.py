from pathlib import Path

import pandas as pd
import streamlit as st


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


st.set_page_config(page_title="Amazon Sales Dashboard", page_icon="📊")
st.title("Amazon Sales Dashboard")
st.caption("This dashboard will summarize Amazon sales trends and product performance once the full view is built.")

data_path = Path(__file__).resolve().parent / "data" / "raw" / "amazon.csv"
raw_df = pd.read_csv(data_path)
cleaned_df = clean_data(raw_df)

before_rows = len(raw_df)
after_rows = len(cleaned_df)
dropped_rows = before_rows - after_rows

col1, col2, col3 = st.columns(3) #splits the page into 3 side by side sections
col1.metric("Total Products", f"{after_rows}")#uses the row count of the cleaned dataframe to display the total number of products
col2.metric("Average Rating", f"{cleaned_df['rating'].mean():.2f}")
col3.metric("Average Discount %", f"{cleaned_df['discount_percentage'].mean():.2f}%")

st.write("Preview of the cleaned data:")
st.dataframe(cleaned_df[["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]].head(5))
