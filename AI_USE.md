# AI Use Log

| Tool Used | What I Asked | What I Kept/Changed/Rejected |
| --- | --- | --- |
| GitHub Copilot Chat | Write a clean_data function to handle messy price (₹, commas), discount percentage (%), rating (non-numeric placeholder), and rating_count (commas, missing values) columns | Kept the function as-is after reviewing the logic. Confirmed the strip-then-convert order of operations (astype(str) then str.replace then pd.to_numeric with errors="coerce"). Deliberately kept the dropna(how="any") approach, which drops a row if any of the five cleaned columns is missing, prioritizing clean/reliable data over maximizing row count. |
