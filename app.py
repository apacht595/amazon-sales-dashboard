from pathlib import Path

import pandas as pd
import plotly.express as px
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

col1, col2, col3 = st.columns(3)
col1.metric("Total Products", f"{after_rows}")
col2.metric("Average Rating", f"{cleaned_df['rating'].mean():.2f}")
col3.metric("Average Discount %", f"{cleaned_df['discount_percentage'].mean():.2f}%")

top_level_categories = cleaned_df["category"].str.split("|").str[0].str.strip()

category_counts = (
    pd.DataFrame({"category": top_level_categories})
    .value_counts()
    .reset_index(name="product_count")
)
category_counts.columns = ["category", "product_count"]

category_ratings = (
    cleaned_df.assign(category=top_level_categories)
    .groupby("category", as_index=False)["rating"]
    .mean()
)

chart1 = px.bar(
    category_counts.head(10),
    x="product_count",
    y="category",
    orientation="h",
    title="Product Count by Category",
)
chart1.update_layout(yaxis={'categoryarray': category_counts['category'].tolist()})

chart2 = px.bar(
    category_ratings.sort_values("rating", ascending=False).head(10),
    x="rating",
    y="category",
    orientation="h",
    title="Average Rating by Category",
)
chart2.update_layout(yaxis={'categoryarray': category_ratings.sort_values('rating', ascending=False)['category'].tolist()})

chart3 = px.scatter(
    cleaned_df,
    x="actual_price",
    y="discounted_price",
    title="Actual Price vs Discounted Price",
    hover_name="product_name",
)
chart3.update_traces(marker=dict(size=8, opacity=0.7))

st.plotly_chart(chart1, use_container_width=True)
st.write(
    "This chart shows which product categories are most represented in the dataset."
    " Categories with the highest counts may indicate where the catalog is most concentrated."
)

st.plotly_chart(chart2, use_container_width=True)
st.write(
    "This chart highlights the categories that tend to receive the strongest customer ratings."
    " Higher bars suggest better perceived quality or satisfaction within those categories."
)

st.plotly_chart(chart3, use_container_width=True)
st.write(
    "This scatter plot compares each product's actual price to its discounted price."
    " Points near the diagonal suggest smaller discounts, while points below it indicate deeper markdowns."
)

st.write("Preview of the cleaned data:")
st.dataframe(cleaned_df[["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]].head(5))
