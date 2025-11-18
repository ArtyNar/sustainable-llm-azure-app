import azure.functions as func
from openai import AzureOpenAI
import logging
import json
import uuid
import requests
import os
from datetime import datetime

app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="send", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
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
    
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")

    if not AZURE_OPENAI_ENDPOINT:
        return func.HttpResponse(
            body=json.dumps({"error": "AZ_OPENAI_ENDPOINT not configured"}),
            status_code=500,
            mimetype="application/json"
        )
    
    if not AZURE_OPENAI_KEY:
        return func.HttpResponse(
            body=json.dumps({"error": "AZ_OPENAI_KEY not configured"}),
            status_code=500,
            mimetype="application/json"
        )
    
    api_version = "2024-12-01-preview"
    deployment = "gpt-4o-mini"

    try:
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_KEY,
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
                    "content": "You are a helpful assistant. The response will be pasted into an HTML div, so make sure you provide HTML formatted prompts. Also, you only have 100 output tokens allowed, so make it short.",
                },
                {
                    "role": "user",
                    "content": prompt_text,
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
        "message": f"{response_text}",
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
    


# @app.function_name(name="SchedulePrompt")
# @app.route(route="schedule", auth_level=func.AuthLevel.ANONYMOUS)
# def get_CI(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Attempting to schedule a prompt.')

#     payload = {
#         "message": f"Scheduled successfully.",
#         "status": "ok"
#     }

#     return func.HttpResponse(
#         body=json.dumps(payload),
#         status_code=200,
#         mimetype="application/json"
#     )


@app.function_name(name="SchedulePrompt")
@app.route(route="schedule", methods=["POST"])
@app.table_output(arg_name="message",
                  connection="TABLE_PROMPT_STORAGE", # Make sure env variable is set 
                  table_name="messages")
def table_out_binding(req: func.HttpRequest, message: func.Out[str]):

    # Get prompt from frontend 
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


    # Create table row 
    data = {
        "PartitionKey": "pending", # Effectively table name
        "RowKey": str(uuid.uuid4()), # Generates a key 
        "Prompt": prompt_text,      
        "Timestamp":  datetime.now(datetime.timezone.utc),
        "CarbonIntensity": 0
    }

    return func.HttpResponse(
        body=json.dumps({"message": f"Something hhappening.","status": "ok"}),
        status_code=200,
        mimetype="application/json"
    )

    table_json = json.dumps(data)
    message.set(table_json)

    return func.HttpResponse(
        body=json.dumps({"message": f"Scheduled successfully.","status": "ok"}),
        status_code=200,
        mimetype="application/json"
    )