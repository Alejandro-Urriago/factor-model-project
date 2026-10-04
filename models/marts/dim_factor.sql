select
    row_number() over (order by factor_name) as factor_id,
    factor_name,
    factor_category,
    factor_short_description
from {{ ref('stg_factor_model__factor_lookup') }}