from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Factor Model Dashboard", layout="wide")

DATA_DIR = Path(__file__).parent

# One app, two places to run:
# - Streamlit in Snowflake: reads the tables with the active Snowflake session.
# - Anywhere else (for example Streamlit Community Cloud): reads the saved CSV files in the data folder.
try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except Exception:
    session = None

if session is not None:
    factor_matrix = session.table("FACTOR_MODEL_PROJECT.ANALYTICS.FACTOR_MATRIX_RESULTS").to_pandas().set_index("Asset")
    long_df = session.table("FACTOR_MODEL_PROJECT.DBT_AURRIAGO.FACT_FACTOR_RETURNS").to_pandas()
else:
    factor_matrix = pd.read_csv(DATA_DIR / "factor_matrix_results.csv").set_index("Asset")
    returns_file = DATA_DIR / "factor_returns.csv"
    long_df = None
    if returns_file.exists():
        wide_file_df = pd.read_csv(returns_file, encoding="utf-8-sig")
        wide_file_df["date"] = pd.to_datetime(wide_file_df["date"], dayfirst=True)
        long_df = wide_file_df.melt(id_vars="date", var_name="FACTOR_NAME", value_name="RETURN_VALUE")
        long_df = long_df.rename(columns={"date": "RETURN_DATE"}).dropna()

factorNames = ['world_equities', 'us_treasuries_10yr', 'high_yield',
               'inflation_protection', 'currency_protection']

AUTHOR_NAME = "Alejandro Urriago, CFA"

# Monthly returns for the time series explorer (optional when running from CSV)
wide_df = None
if long_df is not None:
    wide_df = long_df.pivot(index="RETURN_DATE", columns="FACTOR_NAME", values="RETURN_VALUE").reset_index()
    wide_df.columns = [c.lower() for c in wide_df.columns]
    wide_df = wide_df.rename(columns={"return_date": "Date"})
    wide_df["Date"] = pd.to_datetime(wide_df["Date"])
    wide_df = wide_df[(wide_df["Date"] >= "1997-03-01") & (wide_df["Date"] <= "2012-12-01")].reset_index(drop=True)

st.title("Factor Model Dashboard")
st.markdown("**" + AUTHOR_NAME + "**")
st.caption("5-factor model replicating the Harvard Endowment framework, built with CV-tuned LASSO regression on Snowflake + dbt data.")

col1, col2, col3 = st.columns(3)
col1.metric("Assets modeled", len(factor_matrix))
col2.metric("Factors", len(factorNames))
top_factor = factor_matrix[factorNames].abs().mean().idxmax()
top_factor = top_factor.replace('_', ' ')
top_factor = top_factor.title()
col3.metric("Most influential factor", top_factor)

st.divider()

st.subheader("Factor Loadings Heatmap")


def color_cell(val, vmin=-1, vmax=1):
    t = (val - vmin) / (vmax - vmin)
    if t < 0:
        t = 0
    if t > 1:
        t = 1
    if t < 0.5:
        frac = t / 0.5
        r = int(0x2a + frac * (0xf0 - 0x2a))
        g = int(0x78 + frac * (0xef - 0x78))
        b = int(0xd6 + frac * (0xec - 0xd6))
    else:
        frac = (t - 0.5) / 0.5
        r = int(0xf0 + frac * (0xe3 - 0xf0))
        g = int(0xef - frac * (0xef - 0x49))
        b = int(0xec - frac * (0xec - 0x48))
    style = "background-color: rgb(" + str(r) + "," + str(g) + "," + str(b) + ");"
    style = style + " color: #0b0b0b; text-align: center; padding: 6px;"
    return style


heatmap_header_cells = ""
for f in factorNames:
    label = f.replace('_', ' ')
    label = label.title()
    cell = "<th style='padding:6px;'>"
    cell = cell + label
    cell = cell + "</th>"
    heatmap_header_cells = heatmap_header_cells + cell

html = "<table style='width:100%; border-collapse: collapse; font-family: sans-serif;'>"
row_html = "<tr><th style='text-align:left; padding:6px;'>Asset</th>"
row_html = row_html + heatmap_header_cells
row_html = row_html + "<th style='padding:6px; background-color:#f0f0f0;'>"
row_html = row_html + "Implied Expected Return (Annual)</th></tr>"
html = html + row_html

for asset, row in factor_matrix.iterrows():
    line = "<tr><td style='padding:6px; font-weight:600;'>"
    line = line + str(asset)
    line = line + "</td>"
    html = html + line

    for f in factorNames:
        val = row[f]
        style = color_cell(val)
        cell = "<td style='"
        cell = cell + style
        cell = cell + "'>"
        cell = cell + format(val, ".2f")
        cell = cell + "</td>"
        html = html + cell

    implied_pct = row['Implied Expected Return (Annual)'] * 100
    if implied_pct >= 0:
        implied_color = "#1baf7a"
    else:
        implied_color = "#e34949"

    last_cell = "<td style='padding:6px; text-align:center; font-weight:700;"
    last_cell = last_cell + " color:"
    last_cell = last_cell + implied_color
    last_cell = last_cell + "; background-color:#f7f7f7;'>"
    last_cell = last_cell + format(implied_pct, ".2f")
    last_cell = last_cell + "%</td></tr>"
    html = html + last_cell

html = html + "</table>"
st.markdown(html, unsafe_allow_html=True)
st.caption("Chart by **" + AUTHOR_NAME + "**")

st.divider()

st.subheader("Factor Loadings by Asset")
selected_asset = st.selectbox("Select an asset", factor_matrix.index.tolist(), key="loadings_asset")
asset_loadings = factor_matrix.loc[selected_asset, factorNames]
asset_loadings = asset_loadings.rename(index=lambda f: f.replace('_', ' ').title())
asset_loadings = asset_loadings.sort_values()
st.bar_chart(asset_loadings, horizontal=True)
st.caption("Chart by **" + AUTHOR_NAME + "**")

st.divider()

if wide_df is None:
    st.subheader("Time Series Explorer")
    st.info("Return history is not included in this public version.")
else:
    st.subheader("Time Series Explorer")
    st.caption("Select an asset to see its return history alongside the factors LASSO identified as relevant (non-zero loadings).")

    ts_asset_display = st.selectbox("Select an asset", factor_matrix.index.tolist(), key="ts_asset")
    ts_asset_col = ts_asset_display.lower()
    ts_asset_col = ts_asset_col.replace(' ', '_')

    asset_row = factor_matrix.loc[ts_asset_display, factorNames]
    relevant_factors = asset_row[asset_row.abs() > 0.005].index.tolist()

    if not relevant_factors:
        st.info("No factors with non-zero loadings for this asset.")
    else:
        cols_to_plot = [ts_asset_col] + relevant_factors
        cum_returns = wide_df.set_index("Date")[cols_to_plot]
        cum_returns = (1 + cum_returns).cumprod()

        renamed_cols = []
        for c in cum_returns.columns:
            renamed_cols.append(c.replace('_', ' ').title())
        cum_returns.columns = renamed_cols

        st.line_chart(cum_returns)

        relevant_labels = []
        for f in relevant_factors:
            relevant_labels.append(f.replace('_', ' ').title())

        caption_text = "Relevant factors for "
        caption_text = caption_text + ts_asset_display
        caption_text = caption_text + ": "
        caption_text = caption_text + ", ".join(relevant_labels)
        st.caption(caption_text)
        st.caption("Chart by **" + AUTHOR_NAME + "**")

st.divider()

st.subheader("Adjust Factor Return Assumptions")
st.caption("Move the sliders to see how each asset's implied expected return changes.")

default_premia = {
    'world_equities': 8.0,
    'us_treasuries_10yr': 2.0,
    'high_yield': 5.0,
    'inflation_protection': -0.3,
    'currency_protection': 0.0
}

for f in factorNames:
    key = "premia_" + f
    if key not in st.session_state:
        st.session_state[key] = default_premia[f]

if st.button("Reset to original assumptions"):
    for f in factorNames:
        st.session_state["premia_" + f] = default_premia[f]
    st.rerun()

slider_cols = st.columns(len(factorNames))
user_premia = {}
for col, f in zip(slider_cols, factorNames):
    with col:
        slider_label = f.replace('_', ' ').title()
        slider_key = "premia_" + f
        slider_value = st.slider(
            slider_label,
            min_value=-10.0,
            max_value=15.0,
            step=0.1,
            format="%.1f%%",
            key=slider_key
        )
        user_premia[f] = slider_value / 100

implied_returns = {}
for asset, row in factor_matrix.iterrows():
    total = 12 * row['Intercept']
    for f in factorNames:
        total = total + row[f] * user_premia[f]
    implied_returns[asset] = total

implied_df = pd.DataFrame.from_dict(implied_returns, orient='index', columns=['Implied Expected Return'])
implied_df['Implied Expected Return'] = implied_df['Implied Expected Return'] * 100
implied_df['Implied Expected Return'] = implied_df['Implied Expected Return'].round(2)
implied_df['Implied Expected Return'] = implied_df['Implied Expected Return'].astype(str) + '%'

st.dataframe(implied_df, width="stretch")

implied_pct_chart = {}
for k, v in implied_returns.items():
    implied_pct_chart[k] = v * 100
st.bar_chart(implied_pct_chart)
st.caption("Chart by **" + AUTHOR_NAME + "**")
