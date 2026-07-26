# amazon-sales-dashboard

## Installation and setup

1. Clone the repository:
   ```bash
   git clone <https://github.com/apacht595/amazon-sales-dashboard.git>
   cd amazon-sales-dashboard
   ```

2. Download the dataset from the Amazon Sales Dataset on Kaggle at this address, https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset, and place it at data/raw/amazon.csv. This file is not included in the repository.

3. Install dependencies with uv:
   ```bash
   uv sync
   ```
   If the environment is missing packages, you can add them explicitly with:
   ```bash
   uv add pandas plotly streamlit
   ```
4. Launch the dashboard:
   ```bash
   uv run streamlit run app.py
   ```

## Data cleaning approach

The dashboard uses a `clean_data` function in [app.py](app.py) to prepare the Amazon sales CSV before visualization.

- Currency fields such as `discounted_price` and `actual_price` are stripped of the `₹` symbol and commas, then converted to floats.
- `discount_percentage` values like `64%` are parsed as numeric percentages by removing `%` and casting to float.
- `rating` is converted to numeric, and non-numeric placeholders such as `Not rated` are treated as missing values rather than forcing a guess.
- `rating_count` is cleaned by removing comma separators and converting to numeric, while blank values are also treated as missing.

Rows with unusable values in any of these fields are dropped so the dashboard only receives complete numeric data for analysis. This keeps the charts reliable and avoids silently introducing incorrect values from malformed records.
