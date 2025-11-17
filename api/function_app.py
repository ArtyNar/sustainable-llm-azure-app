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
    
    try:
        req_body = req.get_json()
        prompt_text = req_body.get('prompt')
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON",
            status_code=400
        )
    
    if not prompt_text:
        return func.HttpResponse(
            body=json.dumps({"error": "Please provide a prompt"}),
            status_code=400,
            mimetype="application/json"
        )
    
    logging.info(f'Received prompt: {prompt_text}')
    
    payload = {
        "message": f"You asked: {prompt_text}",
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

        url = "https://api.electricitymaps.com/v3/carbon-intensity/latest?dataCenterRegion=eastus2&dataCenterProvider=azure&disableEstimations=true&emissionFactorType=direct"
        headers={"auth-token": EM_KEY}
        response = requests.get(url,headers=headers)
        response.raise_for_status()

        cur_CI = response.json()["carbonIntensity"]
        cur_zone = response.json()["zone"]
        timestamp = response.json()["datetime"]
        
        payload = {
            "carbonIntensity": cur_CI,
            "zone": cur_zone,
            "zone_name": "PJM Interconnection",
            "timestamp": timestamp,
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