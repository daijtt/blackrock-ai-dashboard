import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ==============================
# Page setup
# ==============================
st.set_page_config(page_title="BlackRock x AI Boom", layout="wide")

# ==============================
# Header
# ==============================
st.title("Is BlackRock Benefiting from the AI Boom?")
st.caption("Market Sensitivity & Risk Dashboard")

# ==============================
# Controls (Top row)
# ==============================
c1, c2, c3, c4 = st.columns([1.2, 1, 1.6, 0.6])

with c1:
    period_label = st.selectbox("Date Range", ["Last 6M", "Last 1Y", "Last 2Y", "Last 3Y","Last 4Y", "Last 5Y"], index=1)

with c2:
    benchmark_label = st.selectbox(
        "Benchmark",
        ["Nasdaq Composite (^IXIC)", "S&P 500 (^GSPC)"],
        index=0
    )

with c3:
    weight_nvda = st.slider("AI Proxy Weights (NVDA vs MSFT)", 0.0, 1.0, 0.5, 0.05)
    weight_msft = 1 - weight_nvda
    st.caption(f"NVDA: {weight_nvda:.0%}  |  MSFT: {weight_msft:.0%}")

with c4:
    refresh = st.button("Refresh")

# Map UI to yfinance period
period_map = {
    "Last 6M": "6mo",
    "Last 1Y": "1y",
    "Last 2Y": "2y",
    "Last 3Y": "3y",
    "Last 4Y": "4y",
    "Last 5Y": "5y",
}
period = period_map[period_label]

benchmark_ticker = "^IXIC" if "IXIC" in benchmark_label else "^GSPC"

# ==============================
# Data loading (robust)
# ==============================
@st.cache_data(ttl=60 * 60, show_spinner=False)  # cache 1 hour
def load_prices(tickers, period):
    """
    Robust loader:
    - auto_adjust=True => Close is adjusted (splits/dividends)
    - handles MultiIndex output from yfinance
    """
    raw = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        group_by="column",
        progress=False,
        threads=True,
    )

    if raw is None or raw.empty:
        return pd.DataFrame()

    # MultiIndex columns: level0 = OHLCV, level1 = ticker
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            prices = raw["Close"].copy()
        elif "Adj Close" in raw.columns.get_level_values(0):
            prices = raw["Adj Close"].copy()
        else:
            return pd.DataFrame()
    else:
        # Non-multiindex fallback
        if "Close" in raw.columns:
            prices = raw[["Close"]].copy()
        elif "Adj Close" in raw.columns:
            prices = raw[["Adj Close"]].copy()
        else:
            return pd.DataFrame()

    prices = prices.dropna(how="all")
    prices.index = pd.to_datetime(prices.index)
    return prices

tickers = ["BLK", "NVDA", "MSFT", benchmark_ticker]

if refresh:
    load_prices.clear()

prices = load_prices(tickers, period)

if prices.empty or prices.shape[0] < 40:
    st.error("No price data returned. Check your internet connection, tickers, or try another period.")
    st.stop()

missing = [t for t in tickers if t not in prices.columns]
if missing:
    st.error(f"Missing tickers in returned data: {missing}. Try again or change the benchmark.")
    st.stop()

# ==============================
# Returns & AI Composite
# ==============================
returns = prices.pct_change().dropna()

# AI Proxy (NVDA/MSFT weights)
returns["AI"] = (weight_nvda * returns["NVDA"]) + (weight_msft * returns["MSFT"])

# Cumulative growth of $1
cumulative = (1 + returns[["BLK", "AI", benchmark_ticker]]).cumprod()

# ==============================
# KPI calculations
# ==============================
def safe_last(x):
    x = x.dropna()
    return x.iloc[-1] if len(x) else np.nan

blk_total = cumulative["BLK"].iloc[-1] - 1
ai_total = cumulative["AI"].iloc[-1] - 1

rolling_corr_30 = returns["BLK"].rolling(30).corr(returns["AI"])
corr_30 = safe_last(rolling_corr_30)

rolling_vol_30 = returns["BLK"].rolling(30).std() * np.sqrt(252)
vol_30 = safe_last(rolling_vol_30)

# Beta + R² (BLK ~ AI)
X = sm.add_constant(returns["AI"])
model = sm.OLS(returns["BLK"], X).fit()
beta = model.params.get("AI", np.nan)
r2 = model.rsquared

# Drawdown (BLK only for clarity)
blk_cum = cumulative["BLK"]
blk_drawdown = (blk_cum / blk_cum.cummax()) - 1

# ==============================
# KPI Row (clean)
# ==============================
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("BLK Return (Selected Period)", f"{blk_total:.2%}")
k2.metric("AI Composite Return (Selected Period)", f"{ai_total:.2%}")
k3.metric("30D Correlation (BLK vs AI)", "—" if pd.isna(corr_30) else f"{corr_30:.2f}")
k4.metric("BLK 30D Volatility (Ann.)", "—" if pd.isna(vol_30) else f"{vol_30:.2%}")
k5.metric("Beta vs AI (OLS)", f"{beta:.2f}")

st.markdown("---")

# ==============================
# Row 1: Performance (left) + Risk (right)
# ==============================
left, right = st.columns([2, 1])

with left:
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(x=cumulative.index, y=cumulative["BLK"], name="BLK"))
    fig_perf.add_trace(go.Scatter(x=cumulative.index, y=cumulative["AI"], name="AI Composite"))
    fig_perf.add_trace(go.Scatter(x=cumulative.index, y=cumulative[benchmark_ticker], name="Benchmark"))

    fig_perf.update_layout(
        title="Performance Comparison (Cumulative Return)",
        xaxis_title="Date",
        yaxis_title="Growth of $1",
        legend_title="Series",
        height=420,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig_perf, use_container_width=True)

with right:
    # Risk Analysis: Rolling volatility (BLK vs AI)
    vol_panel = (returns[["BLK", "AI"]].rolling(30).std() * np.sqrt(252)).dropna()

    fig_risk = px.line(vol_panel, title="Risk Analysis (Rolling Volatility, 30D)")
    fig_risk.update_layout(
        xaxis_title="Date",
        yaxis_title="Annualized Volatility",
        height=220,
        margin=dict(l=10, r=10, t=60, b=10),
        legend_title="Series",
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    # Drawdown (BLK only) — single clean chart (no crowding)
    fig_dd = px.line(blk_drawdown, title="Drawdown (BLK)")
    fig_dd.update_layout(
        xaxis_title="Date",
        yaxis_title="Drawdown",
        height=220,
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_dd, use_container_width=True)

st.markdown("---")

# ==============================
# Row 2: Relationship (left) + Scatter (right)
# ==============================
rel_left, rel_right = st.columns(2)

with rel_left:
    fig_corr = px.line(rolling_corr_30.dropna(), title="Relationship Over Time (Rolling Correlation, 30D)")
    fig_corr.update_layout(
        xaxis_title="Date",
        yaxis_title="Correlation",
        height=320,
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with rel_right:
    df_scatter = returns[["AI", "BLK"]].dropna().rename(columns={"AI": "AI Return", "BLK": "BLK Return"})
    fig_scatter = px.scatter(
        df_scatter,
        x="AI Return",
        y="BLK Return",
        trendline="ols",
        title=f"Sensitivity (Beta) & Fit | R²={r2:.2f} | Beta={beta:.2f}",
    )
    fig_scatter.update_layout(
        xaxis_title="AI Composite Daily Return",
        yaxis_title="BLK Daily Return",
        height=320,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==============================
# Footer notes
# ==============================
st.caption(
    "Data: Yahoo Finance (via yfinance). AI Composite = weighted NVDA/MSFT returns. "
    "Metrics use a 30 trading-day rolling window. Beta estimated via OLS on daily returns."
)
