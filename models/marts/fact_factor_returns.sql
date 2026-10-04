{{ dbt_utils.unpivot(
    relation=ref('stg_factor_model__returns'),
    cast_to='number(10,6)',
    exclude=['return_date'],
    field_name='factor_name',
    value_name='return_value'
) }}