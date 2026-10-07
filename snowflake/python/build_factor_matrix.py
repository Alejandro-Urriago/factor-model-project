"""Builds ANALYTICS.FACTOR_MATRIX_RESULTS: one cross-validated LASSO per asset.

Run inside a Snowflake notebook (needs an active Snowpark session).
Needs factor_model_lib.py in the same folder.
"""
import pandas as pd
from snowflake.snowpark.context import get_active_session

from factor_model_lib import run_factor_model, create_dictionary_for_analysis

SOURCE_TABLE = "FACTOR_MODEL_PROJECT.DBT_AURRIAGO.FACT_FACTOR_RETURNS"
RESULTS_TABLE = "FACTOR_MODEL_PROJECT.ANALYTICS.FACTOR_MATRIX_RESULTS"

factorNames = ['world_equities', 'us_treasuries_10yr', 'high_yield',
               'inflation_protection', 'currency_protection']
assetNames = ['sp500_total_return', 'international_equity', 'us_treasury_20yr',
              'corporate_bond', 'commodity', 'tips']

# Assumed annual factor premia, used to compute each asset's implied return
factor_premia_annual = {
    'world_equities': 0.08, 'us_treasuries_10yr': 0.02, 'high_yield': 0.05,
    'inflation_protection': -0.003, 'currency_protection': 0.0
}
expected_returns_monthly = pd.DataFrame(
    [[factor_premia_annual[f] / 12 for f in factorNames]], columns=factorNames
)


def load_returns(session):
    long_df = session.table(SOURCE_TABLE).to_pandas()
    wide_df = long_df.pivot(index="RETURN_DATE", columns="FACTOR_NAME", values="RETURN_VALUE").reset_index()
    wide_df.columns.name = None
    wide_df = wide_df.rename(columns={"RETURN_DATE": "Date"})
    wide_df.columns = [c if c == "Date" else c.lower() for c in wide_df.columns]
    wide_df["Date"] = pd.to_datetime(wide_df["Date"])
    # March 1997 to December 2012 is the complete, gap-free period.
    # Later data has missing values, which scikit-learn cannot handle.
    wide_df = wide_df[(wide_df["Date"] >= "1997-03-01") & (wide_df["Date"] <= "2012-12-01")]
    return wide_df.reset_index(drop=True)


def build_factor_matrix(data, method='CVLasso', methodOptions=None):
    rows = []
    for asset in assetNames:
        options = create_dictionary_for_analysis(method, methodOptions or {'n_folds': 5})
        options['date'] = 'Date'
        model = run_factor_model(data, asset, factorNames, method, options)
        implied_return_annual = 12 * model.predict(expected_returns_monthly)[0]
        rows.append([model.intercept_] + list(model.coef_) + [implied_return_annual])
    cols = ['Intercept'] + factorNames + ['Implied Expected Return (Annual)']
    index = [a.replace('_', ' ').title() for a in assetNames]
    return pd.DataFrame(rows, columns=cols, index=index).round(3)


def save_results(session, factor_matrix):
    result_df = session.create_dataframe(
        factor_matrix.reset_index().rename(columns={'index': 'Asset'})
    )
    result_df.write.save_as_table(RESULTS_TABLE, mode="overwrite")


if __name__ == "__main__":
    session = get_active_session()
    wide_df = load_returns(session)
    factor_matrix = build_factor_matrix(wide_df)
    print(factor_matrix)
    save_results(session, factor_matrix)
