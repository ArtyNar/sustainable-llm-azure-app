import azure.functions as func
import logging
import json
import requests
import os
from openai import AzureOpenAI

app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="send", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        req_body = req.get_json()
        prompt_text = req_body.get('prompt')
    except Exception as e:
        logging.error(f"JSON parsing error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )


    if not prompt_text or prompt_text == "":
        return func.HttpResponse(
            body=json.dumps({"error": "Please provide a prompt"}),
            status_code=400,
            mimetype="application/json"
        )
    
    logging.info(f'Received prompt: {prompt_text}')
    
    AZ_OPENAI_ENDPOINT = os.environ.get("AZ_OPENAI_ENDPOINT")
    AZ_OPENAI_KEY = os.environ.get("AZ_OPENAI_KEY")

    api_version = "2024-12-01-preview"
    deployment = "gpt-4o-mini"

    try:
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=AZ_OPENAI_ENDPOINT,
            api_key=AZ_OPENAI_KEY,
        )
    except Exception as e:
        logging.error(f"JSON parsing error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to connect to Azure OpenAI"}),
            status_code=400,
            mimetype="application/json"
        )
    
    try:   
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "I am going to Paris, what should I see?",
                }
            ],
            max_tokens=100,
            temperature=1.0,
            top_p=1.0,
            model=deployment
        )
    except Exception as e:
        logging.error(f"JSON parsing error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get AZAI response"}),
            status_code=400,
            mimetype="application/json"
        )
    
    response_text = response.choices[0].message.content


    payload = {
        "message": f"You asked: {prompt_text}\n Response: {AZ_OPENAI_ENDPOINT}",
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