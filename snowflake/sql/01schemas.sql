-- 01_schemas.sql
-- Creates the database and the schemas created by hand.
-- Note: the PROD and DBT_AURRIAGO schemas are created by dbt, not here.

CREATE DATABASE IF NOT EXISTS FACTOR_MODEL_PROJECT;

-- RAW: landing zone for source data, loaded as-is, no transformations
CREATE SCHEMA IF NOT EXISTS FACTOR_MODEL_PROJECT.RAW
    COMMENT = 'Raw, untransformed source data. No business logic applied.';

-- ANALYTICS: model results written by the Python factor model
CREATE SCHEMA IF NOT EXISTS FACTOR_MODEL_PROJECT.ANALYTICS
    COMMENT = 'Output of the factor model (LASSO regression), read by the Streamlit app.';
