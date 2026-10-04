select
    date as return_date,
    world_equities,
    us_treasuries_10yr,
    high_yield,
    inflation_protection,
    currency_protection,
    us_equity,
    sp500_total_return,
    sp500,
    international_equity,
    us_treasury_20yr,
    corporate_bond,
    real_estate,
    commodity,
    tips
from {{ source('factor_model', 'returns') }}