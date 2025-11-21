from flask import Flask, render_template, request, jsonify
from fetchers import get_inflation_and_interest
from forecast import project_costs, loan_costs

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            groceries = float(request.form.get("groceries", "0"))
        except:
            groceries = 0.0

        # Fetch latest macro data (interest, inflation) - implementation in fetchers.py
        macro = get_inflation_and_interest()

        # Compute projections
        projection = project_costs(groceries, macro['inflation_rate'])

        # Example loan calc default values
        loan = loan_costs(principal=10000, annual_rate=macro['interest_rate'], years=5)
        result = {
            "macro": macro,
            "projection": projection,
            "loan": loan
        }
    return render_template("index.html", result=result)

# API endpoint
@app.route("/api/convert", methods=["GET"])

def api_convert():
    # Example API to return macro data
    macro = get_inflation_and_interest()
    return jsonify(macro)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)