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
st.markdown(
    """
    <style>
        .stApp { padding-top: 0.4rem; padding-left: 0; padding-right: 0; }
        .block-container { padding-top: 1rem; padding-left: 0.4rem; padding-right: 0.4rem; max-width: 100%; }
        .stMetric { background: #f8f9fa; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 0.4rem 0.6rem; }
        .stTitle {
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            line-height: 1.15 !important;
            margin-bottom: 0.3rem !important;
            padding-top: 0.1rem !important;
            font-size: 2.2rem !important;
        }
        .stCaption { font-size: 0.95rem; color: #6b7280; }
        div[data-testid="stHorizontalBlock"] > div { gap: 0.3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("Amazon Sales Dashboard")
st.caption("This dashboard summarizes Amazon sales trends and product performance")

data_path = Path(__file__).resolve().parent / "data" / "raw" / "amazon.csv"
raw_df = pd.read_csv(data_path)
cleaned_df = clean_data(raw_df)

before_rows = len(raw_df)
after_rows = len(cleaned_df)
dropped_rows = before_rows - after_rows

metric_col1, metric_col2, metric_col3, preview_col = st.columns([1, 1, 1, 2.2])
metric_col1.metric("Total Products", f"{after_rows}")
metric_col2.metric("Average Rating", f"{cleaned_df['rating'].mean():.2f}")
metric_col3.metric("Average Discount %", f"{cleaned_df['discount_percentage'].mean():.2f}%")

with preview_col:
    st.markdown("<div style='font-size: 0.8rem; font-weight: 600; margin-bottom: 0.2rem;'>Preview of the cleaned data</div>", unsafe_allow_html=True)
    preview_df = cleaned_df[["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]].head(5)
    preview_html = preview_df.to_html(index=False, escape=False)
    st.markdown(
        f"""
        <div style="font-size: 0.6rem; line-height: 0.95; margin: 0; padding: 0; width: 100%;">
            {preview_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

top_level_categories = cleaned_df["category"].str.split("|").str[0].str.strip()

category_counts = (
    pd.DataFrame({"category": top_level_categories})
    .value_counts()
    .reset_index(name="product_count")
)
category_counts.columns = ["category", "product_count"]
category_counts = category_counts.sort_values("product_count", ascending=False).reset_index(drop=True)

category_ratings = (
    cleaned_df.assign(category=top_level_categories)
    .groupby("category", as_index=False)["rating"]
    .mean()
)
category_ratings = category_ratings.merge(
    category_counts[["category", "product_count"]],
    on="category",
    how="left",
)
category_ratings = category_ratings[category_ratings["product_count"] > 30].sort_values(
    "rating", ascending=False
).reset_index(drop=True)

chart1 = px.bar(
    category_counts.head(10),
    x="category",
    y="product_count",
    title="Product Count by Category",
)
chart1.update_layout(xaxis_title="Category", yaxis_title="Product Count")
chart1.update_traces(text=category_counts["product_count"], textposition="outside")

chart2 = px.bar(
    category_ratings.head(10),
    x="category",
    y="rating",
    title="Average Rating by Category",
)
chart2.update_layout(xaxis_title="Category", yaxis_title="Average Rating")
chart2.update_traces(text=category_ratings["rating"].round(2), textposition="outside")

chart3 = px.scatter(
    cleaned_df,
    x="actual_price",
    y="discounted_price",
    title="Actual Price vs Discounted Price",
    hover_name="product_name",
)
chart3.update_traces(marker=dict(size=8, opacity=0.7))

chart_col1, chart_col2, chart_col3 = st.columns(3)

with chart_col1:
    st.plotly_chart(chart1, use_container_width=True)
    st.caption(
        "This chart shows which product categories are most represented in the dataset."
        " Categories with the highest counts may indicate where the catalog is most concentrated."
    )

with chart_col2:
    st.plotly_chart(chart2, use_container_width=True)
    st.caption(
        "This chart highlights the categories that tend to receive the strongest customer ratings."
        " Higher bars suggest better perceived quality or satisfaction within those categories."
    )

with chart_col3:
    st.plotly_chart(chart3, use_container_width=True)
    st.caption(
        "This scatter plot compares each product's actual price to its discounted price."
        " Points near the diagonal suggest smaller discounts, while points below it indicate deeper markdowns."
    )
