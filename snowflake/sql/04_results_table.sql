/*
04_results_table.sql
Model output table. Written by the Python LASSO model, read by the Streamlit app.
One row per asset: regression intercept, 5 factor loadings, implied annual return.
Note: quoted column names are case-sensitive in Snowflake.
*/

CREATE TABLE IF NOT EXISTS FACTOR_MODEL_PROJECT.ANALYTICS.FACTOR_MATRIX_RESULTS (
    "Asset"                            VARCHAR(16777216),
    "Intercept"                        FLOAT,
    "world_equities"                   FLOAT,
    "us_treasuries_10yr"               FLOAT,
    "high_yield"                       FLOAT,
    "inflation_protection"             FLOAT,
    "currency_protection"              FLOAT,
    "Implied Expected Return (Annual)" FLOAT
);
