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

# ----------------------------
# Helper function for Inflation forecast
# ----------------------------

def forecast_to_json(fc, ci):
    """ Convert forecast results to JSON-serializable format."""
    return {
        "forecast": {str(k): float(v) for k, v in fc.to_dict().items()},
        "confidence_intervals": {
            "lower": {str(k): float(v) for k, v in ci["lower"].to_dict().items()},
            "upper": {str(k): float(v) for k, v in ci["upper"].to_dict().items()}
        }
    }

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok", "message": "Macro Insights API is running"})


# ---------------------------
# South Africa Inflation Data
# ---------------------------

@app.route("/api/sa/inflation")
def sa_inflation():
    df = sa.fetch_inflation() # Inflation (%)
    if df.empty:
        return jsonify({"error": "No inflation data found"}), 404
    
    return df.to_json(orient="records", date_format="iso")


# ---------------------------
# South African Inflation Forecast
# ---------------------------

@app.route("/api/sa/inflation/forecast")
def sa_inflation_forecast():
    try:
        df = sa.fetch_inflation()
        series = series_from_df(df)

        model = AutoARIMAForecaster()
        model.fit(series)

        fc, ci = model.forecast(steps=5)

        return jsonify(forecast_to_json(fc, ci))

    except Exception as e:
        return jsonify({
            "error": "Forecast failed",
            "details": str(e)
        }), 500



# -----------------------------
# South African Interest Rates
# -----------------------------

@app.route("/api/sa/rates")
def sa_rates():
    repo = sa.fetch_lending_rate()
    if repo.empty:
        return jsonify({"error": "No interest rate data found"}), 404
    
    return repo.to_json(orient="records", date_format="iso")


# ---------------------------
# South African GDP Growth
# ---------------------------

@app.route("/api/sa/gdp")
def sa_gdp():
    df = sa.fetch_gdp_growth()

    if df.empty:
        return jsonify({"error": "No South Africa GDP data found"}), 404

    return df.to_json(orient="records", date_format="iso")


# -----------------------------
# US Inflation Data
# -----------------------------

@app.route("/api/us/inflation")
def us_inflation():
    df = us.fetch_inflation()  # Inflation (% y/y)

    if df.empty:
        return jsonify({"error": "No US inflation data found"}), 404

    return df.to_json(orient="records", date_format="iso")


# ---------------------------
# US Inflation Forecast
# ---------------------------

@app.route("/api/us/inflation/forecast")
def us_inflation_forecast():
    try:
        df = us.fetch_inflation()
        series = series_from_df(df)

        model = AutoARIMAForecaster()
        model.fit(series)

        fc, ci = model.forecast(steps=5)

        return jsonify(forecast_to_json(fc, ci))

    except Exception as e:
        return jsonify({
            "error": "Forecast failed",
            "details": str(e)
        }), 500



# ---------------------------
# US GDP Growth
# ---------------------------

@app.route("/api/us/gdp")
def us_gdp():
    df = us.fetch_gdp_growth()

    if df.empty:
        return jsonify({"error": "No US GDP data found"}), 404

    return df.to_json(orient="records", date_format="iso")

# ---------------------------
# US REAL INTEREST RATES
# ---------------------------

@app.route("/api/us/real_rates")
def us_real_rates():
    df = us.fetch_real_interest_rate()

    if df.empty:
        return jsonify({"error": "No real interest rates data found"}), 404

    return df.to_json(orient="records", date_format="iso")

# -----------------------------
# Start Server
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)