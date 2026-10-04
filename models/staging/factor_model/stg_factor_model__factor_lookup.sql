select
    factor_name,
    factor_category,
    factor_short_description
from {{ source('factor_model', 'factor_lookup') }}