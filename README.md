# amazon-sales-dashboard

## Data cleaning approach

The dashboard uses a `clean_data` function in [app.py](app.py) to prepare the Amazon sales CSV before visualization.

- Currency fields such as `discounted_price` and `actual_price` are stripped of the `₹` symbol and commas, then converted to floats.
- `discount_percentage` values like `64%` are parsed as numeric percentages by removing `%` and casting to float.
- `rating` is converted to numeric, and non-numeric placeholders such as `Not rated` are treated as missing values rather than forcing a guess.
- `rating_count` is cleaned by removing comma separators and converting to numeric, while blank values are also treated as missing.

Rows with unusable values in any of these fields are dropped so the dashboard only receives complete numeric data for analysis. This keeps the charts reliable and avoids silently introducing incorrect values from malformed records.
