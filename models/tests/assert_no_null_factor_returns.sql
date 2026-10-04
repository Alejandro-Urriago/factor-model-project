-- A null (or missing) return value means a factor-fund NaN slipped through
-- the pipeline undetected. This broke the Python regression earlier when
-- the data source had gaps from ~2015 onward, so this test catches that
-- condition at the dbt layer instead of downstream in the model.
-- Scoped to 1997-03-01 to 2012-12-01, the clean period used in the
-- regression model (nulls outside this window are expected and not tested here).
-- dbt singular test convention: the test FAILS if this query returns any rows.

select
    return_date,
    factor_name,
    return_value
from {{ ref('fact_factor_returns') }}
where return_value is null
and return_date between '1997-03-01' and '2012-12-01'