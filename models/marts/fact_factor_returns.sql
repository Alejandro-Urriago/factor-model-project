with unpivoted as (
    {{ dbt_utils.unpivot(
        relation=ref('stg_factor_model__returns'),
        cast_to='number(10,6)',
        exclude=['return_date'],
        field_name='factor_name',
        value_name='return_value'
    ) }}
)

select
    u.return_date,
    f.factor_id,
    lower(u.factor_name) as factor_name,
    u.return_value
from unpivoted u
left join {{ ref('dim_factor') }} f
    on lower(u.factor_name) = f.factor_name