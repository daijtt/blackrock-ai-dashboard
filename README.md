
# Is BlackRock Benefiting from the AI Boom?
## Market Sensitivity & Risk Dashboard (Streamlit)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) 
![Streamlit](https://img.shields.io/badge/Streamlit-Live%20App-ff4b4b)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-6f42c1)
![License](https://img.shields.io/badge/License-MIT-green)

Live Dashboard: https://blackrock-ai-dashboard.streamlit.app/  
Source Code: https://github.com/daijtt/blackrock-ai-dashboard  

---

## Dashboard Preview

### Live Demo Video


https://github.com/user-attachments/assets/c4387a1e-49b1-42f8-806d-bd1d386e4ac2



---

### Dashboard Screenshot

![image alt](https://github.com/daijtt/blackrock-ai-dashboard/blob/ca6513862f881b7400150db6e3e4038f03865ecb/assets/dashboard-full.png)
---

## Executive Summary

This project evaluates whether BlackRock (BLK) has materially benefited from the recent AI-driven equity boom.

Using publicly available market data, a dynamic AI proxy index was constructed to measure BlackRock’s performance, volatility, and statistical sensitivity relative to AI-driven equities.

The analysis indicates moderate exposure, but not structural dependence, on AI market momentum.

---

## Research Question

To what extent does AI sector growth influence BlackRock’s stock performance and risk profile?

---

## Project Overview

Recent years have seen substantial equity returns driven by AI-related companies, particularly within technology-heavy indices.

BlackRock, however, is a diversified institutional asset manager rather than a pure AI growth company.

This project investigates whether BlackRock meaningfully moves with AI sector performance, and if so, how strong and consistent that relationship is.

The result is a live, interactive financial dashboard that quantifies performance, risk, and statistical exposure.

---

## Data Sources

All data used in this project is publicly available and retrieved live from Yahoo Finance using the `yfinance` Python library.

Tickers used:
- BLK — BlackRock Inc.
- NVDA — NVIDIA Corporation
- MSFT — Microsoft Corporation
- ^IXIC — Nasdaq Composite Index
- ^GSPC — S&P 500 Index

Data characteristics:
- Daily adjusted closing prices
- Automatically adjusted for splits and dividends using `auto_adjust=True`

No paid APIs were used.

---

## Methodology

### 1. Return Calculation

Daily returns are computed as:

```
rₜ = (Pₜ / Pₜ₋₁) − 1
```

Where:
- Pₜ is the adjusted closing price at time t  
- rₜ represents the daily return  

Returns are then converted into cumulative growth series to represent “growth of $1” for intuitive performance comparison.

---

### 2. AI Proxy Construction

Because no free official AI index is available, a custom composite AI proxy was constructed:

```
AIₜ = w × r_NVDA,ₜ + (1 − w) × r_MSFT,ₜ
```

Where:
- w is dynamically controlled via a dashboard slider  
- NVDA represents high AI hardware exposure  
- MSFT represents AI-integrated enterprise exposure  

This structure allows sensitivity testing rather than assuming a fixed AI definition.

---

### 3. Regression & Sensitivity Analysis

An Ordinary Least Squares (OLS) regression is applied to measure exposure:

```
r_BLK,ₜ = α + β × r_AI,ₜ
```

Where:
- β (Beta) measures BlackRock’s sensitivity to AI returns  
- R² measures how much of BlackRock’s return variability is explained by AI movements  

Additionally:
- Rolling 30-day correlation measures relationship stability
- Rolling 30-day annualized volatility measures short-term risk
- Maximum drawdown captures peak-to-trough decline

---

## Financial Metrics Included

Performance:
- Period return (6 months to 5 years)
- Cumulative growth comparison

Risk:
- 30-day rolling annualized volatility
- Maximum drawdown

Relationship:
- Rolling correlation
- Beta
- R²
- Regression scatter with fitted trendline

---

## Dashboard Features

- Interactive time window selection (6 months to 5 years)
- Benchmark comparison (Nasdaq or S&P 500)
- Adjustable AI proxy weighting
- Performance comparison chart
- Risk panel (volatility and drawdown)
- Sensitivity analysis with regression modeling
- Live data refresh

The dashboard is fully interactive and publicly accessible.

---

## Key Insights

Across most time periods and AI weighting configurations:

- BlackRock exhibits moderate sensitivity to AI sector returns.
- AI explains only a portion of BlackRock’s price movement (R² typically below 0.30).
- BlackRock behaves more like a diversified financial institution than a momentum-driven AI stock.
- Increasing the weight of NVIDIA significantly increases AI proxy volatility, but does not proportionally increase BlackRock sensitivity.

Conclusion:

BlackRock benefits indirectly from AI-driven market conditions, but its stock performance is largely influenced by broader market and institutional factors rather than pure AI momentum.

---

## Assumptions & Limitations

- The AI proxy is simplified (NVDA + MSFT only).
- Correlation and regression do not imply causation.
- Macroeconomic variables such as interest rates and liquidity conditions are not explicitly modeled.
- Live data availability depends on Yahoo Finance uptime.

Future improvements could include:
- Incorporating AUM growth data
- Adding macroeconomic overlays
- Expanding the AI proxy basket

---

## Tools Used

- Python  
- Streamlit  
- yfinance  
- pandas  
- numpy  
- plotly  
- statsmodels  

---

## Run Locally

```
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Objective

This project demonstrates:

- Financial modeling capability  
- Quantitative analysis  
- Interactive visualization design  
- Clear communication of technical results to non-technical stakeholders  




