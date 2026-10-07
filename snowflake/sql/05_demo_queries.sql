-- 05_demo_queries.sql
-- Demo queries on the dbt output tables (PROD schema).

/* NOTE: The table structure is unpivoted. Each row is one factor on one date
   (columns: return_date, factor_name, return_value). In the raw table, each
   factor was its own column, so this filter was not possible. */
SELECT *
FROM FACTOR_MODEL_PROJECT.PROD.FACT_FACTOR_RETURNS AS a
WHERE a.return_date = (
    SELECT MIN(b.return_date)
    FROM FACTOR_MODEL_PROJECT.PROD.FACT_FACTOR_RETURNS AS b
)
ORDER BY a.factor_name ASC;

/* Because factor_name is now a value, WHERE can select one factor. */
SELECT *
FROM FACTOR_MODEL_PROJECT.PROD.FACT_FACTOR_RETURNS AS a
WHERE a.factor_name = 'commodity'
ORDER BY a.return_date
LIMIT 20;

/* Because factor_id is a key, LEFT JOIN adds each factor's category and
   description from the dimension table. */
SELECT a.return_date, a.factor_name, a.return_value,
       b.factor_category, b.factor_short_description
FROM FACTOR_MODEL_PROJECT.PROD.FACT_FACTOR_RETURNS AS a
LEFT JOIN FACTOR_MODEL_PROJECT.PROD.DIM_FACTOR AS b
    ON a.factor_id = b.factor_id
ORDER BY a.return_date, a.factor_name
LIMIT 20;
