# === Dependencies to install ===
# pip install Flask

from flask import Flask, request, jsonify
from functools import wraps
import re
from datetime import datetime

app = Flask(__name__)

USERNAME = "user"
PASSWORD = "password"

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

def validate_json_and_dates(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Invalid JSON payload"}), 422
       
        payload = request.get_json()
        if "date" not in payload or "amount" not in payload:
            return jsonify({"error": "Missing required fields: 'date' and 'amount'"}), 422
       
        if not isinstance(payload.get("date"), str) or not isinstance(payload.get("amount"), (int, float)):
            return jsonify({"error": "Invalid data types: 'date' must be a string and 'amount' must be a number"}), 422
       
        if not is_valid_date_format(payload["date"]):
            return jsonify({"error": f"Invalid date format for 'date': {payload['date']}. Use 'DD-MM-YYYY'"}), 422

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        if start_date and not is_valid_date_format(start_date):
            return jsonify({"error": f"Invalid date format for 'start_date': {start_date}. Use 'DD-MM-YYYY'"}), 422
        if end_date and not is_valid_date_format(end_date):
            return jsonify({"error": f"Invalid date format for 'end_date': {end_date}. Use 'DD-MM-YYYY'"}), 422
       
        return func(*args, **kwargs)
    return wrapper

def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

@app.route("/api/client/<client_id>/transactions", methods=["POST"])
@authenticate
@validate_json_and_dates
def process_transaction(client_id):
    payload = request.get_json()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
   
    response = {
        "message": "Transaction processed successfully",
        "client_id": client_id,
        "payload": payload,
        "query_parameters": {"start_date": start_date, "end_date": end_date}
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)