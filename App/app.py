from flask import Flask, jsonify
from fetchers.south_africa import SouthAfricaFetcher
from fetchers.us_fetcher import USFetcher
from forecasting.classical import AutoARIMAForecaster, series_from_df

app = Flask(__name__)

sa = SouthAfricaFetcher()
us = USFetcher()

# ----------------------------
# Health check route
# ----------------------------

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok", "message": "Macro Insights API is running"})


# ---------------------------
# South Africa Inflation Data
# ---------------------------

@app.route("/api/sa/inflation")
def sa_inflation():
    df = sa.fetch_inflation("FP.CPI.TOTL.ZG") # Inflation (%)
    if df.empty:
        return jsonify({"error": "No inflation data found"}), 404
    
    return df.to_json(orient="records")


# ---------------------------
# South African Inflation Forecast
# ---------------------------

@app.route("/api/sa/inflation/forecast")
def sa_inflation_forecast():
    df = sa.fetch_inflation("FP.CPI.TOTL.ZG")
    if df.empty:
        return jsonify({"error": "No inflation data found"}), 404
    
    series = series_from_df(df)

    model = AutoARIMAForecaster()
    model.fit(series)

    fc, ci = model.forecast(steps=5)

    output = {
        "forecast": fc.to_dict(),
        "confidence_intervals": {
            "lower": ci["lower"].to_dict(),
            "upper": ci["upper"].to_dict()
        }
    }

    return jsonify(output)


# -----------------------------
# South African Interest Rates
# -----------------------------

@app.route("/api/sa/rates")
def sa_rates():
    repo = sa.fetch_lending_rate("FR.INR.LEND")
    if repo.empty:
        return jsonify({"error": "No interest rate data found"}), 404
    
    return repo.to_json(orient="records")


# ---------------------------
# South African GDP Growth
# ---------------------------

@app.route("/api/sa/gdp")
def sa_gdp():
    df = sa.fetch_gdp_growth("NY.GDP.MKTP.KD.ZG")

    if df.empty:
        return jsonify({"error": "No South Africa GDP data found"}), 404

    return df.to_json(orient="records")


# -----------------------------
# US Inflation Data
# -----------------------------

@app.route("/api/us/inflation")
def us_inflation():
    df = us.fetch_inflation("FP.CPI.TOTL.ZG")  # Inflation (% y/y)

    if df.empty:
        return jsonify({"error": "No US inflation data found"}), 404

    return df.to_json(orient="records")


# ---------------------------
# US Inflation Forecast
# ---------------------------

@app.route("/api/us/inflation/forecast")
def us_inflation_forecast():
    df = us.fetch_inflation("FP.CPI.TOTL.ZG")

    if df.empty:
        return jsonify({"error": "No US inflation data found"}), 404

    series = series_from_df(df)

    model = AutoARIMAForecaster()
    model.fit(series)

    fc, ci = model.forecast(steps=5)

    return jsonify({
        "forecast": fc.to_dict(),
        "confidence_intervals": {
            "lower": ci["lower"].to_dict(),
            "upper": ci["upper"].to_dict()
        }
    })

# ---------------------------
# US Interest Rates (Lending Rate)
# ---------------------------

@app.route("/api/us/rates")
def us_rates():
    df = us.fetch_lending_rate("FR.INR.LEND")

    if df.empty:
        return jsonify({"error": "No US interest-rate data found"}), 404

    return df.to_json(orient="records")


# ---------------------------
# US GDP Growth
# ---------------------------

@app.route("/api/us/gdp")
def us_gdp():
    df = us.fetch_gdp_growth("NY.GDP.MKTP.KD.ZG")

    if df.empty:
        return jsonify({"error": "No US GDP data found"}), 404

    return df.to_json(orient="records")

# ---------------------------
# US REAL INTEREST RATES
# ---------------------------

@app.route("/api/us/real_rates")
def us_gdp():
    df = us.fetch_real_interest_rate("FR.INR.RINR")

    if df.empty:
        return jsonify({"error": "No real interest rates data found"}), 404

    return df.to_json(orient="records")

# -----------------------------
# Start Server
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)