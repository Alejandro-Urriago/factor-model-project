# Factor Model Dashboard

A 5-factor model replicating the Harvard Endowment framework, built end to end on Snowflake.
Raw returns are modelled with dbt, a cross-validated LASSO regression estimates each asset's factor loadings,
and a Streamlit app lets you explore the results and test your own return assumptions.

**Author:** Alejandro Urriago, CFA

## What it does

- Loads monthly returns for 6 assets and 5 factors into Snowflake
- Models the data with dbt (staging, dimensions, fact table, tests)
- Fits a CV-tuned LASSO per asset to get factor loadings and an implied annual expected return
- Shows the results in a Streamlit dashboard: loadings heatmap, loadings by asset, time series explorer, and sliders to change factor return assumptions

## Data flow

```
CSV files -> RAW tables -> dbt models -> FACT_FACTOR_RETURNS
          -> Python LASSO -> ANALYTICS.FACTOR_MATRIX_RESULTS -> Streamlit app
```

## Factors and assets

- **Factors:** world equities, US treasuries 10yr, high yield, inflation protection, currency protection
- **Assets:** S&P 500 total return, international equity, US treasury 20yr, corporate bond, commodity, TIPS
- **Period used for the model:** March 1997 to December 2012 (the complete period with no missing values)

## Repo structure

```
snowflake/sql/     Database, schemas, raw tables, data load, results table, demo queries
dbt/               dbt project (sources, staging, dimensions, fact table, tests)
python/            LASSO model script, helper library, requirements
streamlit_app/     Dashboard code and Snowflake deployment settings
results/           Model output as CSV
```

## How to run

1. Run the files in `snowflake/sql/` in order (01 to 04).
2. Run the dbt project to build `FACT_FACTOR_RETURNS`.
3. Run `python/build_factor_matrix.py` in a Snowflake notebook. It writes `ANALYTICS.FACTOR_MATRIX_RESULTS`.
4. Deploy the app in `streamlit_app/` as a Streamlit in Snowflake app.

## Results

The model output is saved in `results/factor_matrix_results.csv`.
Each row is an asset: intercept, five factor loadings, and implied expected return (annual).

## Tech stack

Snowflake, dbt, Python (pandas, scikit-learn), Streamlit in Snowflake

## Notes

- The Streamlit app only runs inside Snowflake, because it reads its data through a Snowflake session.
- Factor premia used for the implied returns are assumptions (the app lets you change them with sliders).
