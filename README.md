# 📊 Macro_Insights

**Macro_Insights** is a full-stack Python application that analyzes and forecasts key macroeconomic indicators for South Africa and the United States, with a focus on real-world financial impact.

Macroeconomic variables such as inflation, interest rates, and GDP growth drive financial markets, household costs, and investment decisions.  
This project bridges economic theory, data science, and software engineering into a single production-ready system.

---

## 🚀 Features

### 🌍 Macroeconomic Data
- Inflation (CPI)
- GDP Growth
- Interest / Policy Rates
- Coverage: **South Africa 🇿🇦 & United States 🇺🇸**

### 📈 Forecasting
- ARIMA-based inflation forecasting
- Confidence intervals (uncertainty modeling)
- Multi-step future projections

### 🧮 Financial Impact Tools
- Grocery inflation cost estimator
- Loan repayment calculator based on interest rates

### 🖥️ Interactive Dashboard
- Country-specific economic views
- Forecast visualization
- Clean, responsive UI via Streamlit

---

## 🧠 Why This Project Matters

Macroeconomics moves:
- Equity markets
- Bond yields
- Currency valuations
- Household purchasing power

Understanding **how economic data evolves and how it affects real costs** is essential for anyone working in:
- Data Science
- Finance
- Economics
- Quantitative analysis

Macro_Insights was built to explore that intersection using real data and real forecasting methods.

Here's the link - https://macro-insights.streamlit.app/

---

## 🏗️ Architecture

```text
Macro_Insights/
│
├── app/                      # Backend (Flask API)
│   ├── fetchers/             # Country-specific data fetchers
│   ├── forecasting/          # ARIMA forecasting logic
│   ├── utils/                # Helpers & transformers
│   ├── app.py                # API entry point
│   └── requirements.txt
│
├── frontend/
│   └── streamlit/
│       ├── app.py            # Streamlit dashboard
│       └── requirements.txt
│
├── docker-compose.yml
├── Dockerfile
└── README.md

