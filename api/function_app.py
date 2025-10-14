import azure.functions as func
import logging
import json
import requests
import os

app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="send", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    payload = {
        "message": "This HTTP triggered function executed successfully.",
        "status": "ok"
    }

    return func.HttpResponse(
        body=json.dumps(payload),
        status_code=200,
        mimetype="application/json"
    )

@app.function_name(name="GetCarbonIntensity")
@app.route(route="carbon-intensity", auth_level=func.AuthLevel.ANONYMOUS)
def get_CI(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching carbon intensity data.')


    try:
        EM_KEY = os.environ.get("ELECTRICITY_MAPS_API_KEY")

        if not EM_KEY:
            return func.HttpResponse(
                body=json.dumps({"error": "API key not configured"}),
                status_code=500,
                mimetype="application/json"
            )

        url = "https://api.electricitymaps.com/v3/carbon-intensity/latest?zone=US-MIDA-PJM"
        headers={"auth-token": EM_KEY}
        response = requests.get(url,headers=headers)
        response.raise_for_status()

        cur_CI = response.json()["carbonIntensity"]

        payload = {
            "carbonIntensity": cur_CI,  # More descriptive key
            "zone": "US-MIDA-PJM",
            "zone_name": "PJM Interconnection",
            "timestamp": response.json().get("datetime"),  # Useful context
            "status": "ok"
        }

        return func.HttpResponse(
            body=json.dumps(payload),
            status_code=200,
            mimetype="application/json"
        )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching carbon intensity: {str(e)}")

        return func.HttpResponse(
            body=json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            mimetype="application/json"
        )