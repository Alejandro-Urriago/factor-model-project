select distinct
    return_date,
    year(return_date) as year,
    month(return_date) as month,
    quarter(return_date) as quarter
from {{ ref('fact_factor_returns') }}