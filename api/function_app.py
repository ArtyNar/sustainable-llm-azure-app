import azure.functions as func
from openai import AzureOpenAI
import logging
import json
import uuid
import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from utils import get_cur_CI

app = func.FunctionApp()

@app.function_name(name="sendLLM")
@app.route(route="send", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def sendLLM(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        req_body = req.get_json()
        prompt_text = req_body.get('prompt')
        model = req_body.get('model')
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
    deployment = model

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
    out_tokens = response.usage.completion_tokens

    payload = {
        "message": f"{response_text}",
        "out_tokens": f"{out_tokens}",
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

        cur_CI, cur_zone, timestamp = get_cur_CI(EM_KEY)

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
    
@app.function_name(name="SchedulePrompt")
@app.route(route="schedule", methods=["POST"])
@app.table_output(arg_name="message",
                  connection="TABLE_PROMPT_STORAGE", # Make sure env variable is set 
                  table_name="prompttable")
def table_out_binding(req: func.HttpRequest, message: func.Out[str]):

    # Get prompt from frontend 
    try:
        req_body = req.get_json()
        prompt_text = req_body.get('prompt')
        schedule = req_body.get('schedule')
        model = req_body.get('model')

    except Exception as e:
        logging.error(f"JSON parsing error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )
    
    
    try:
        EM_KEY = os.environ.get("ELECTRICITY_MAPS_API_KEY")

        if not EM_KEY:
            return func.HttpResponse(
                body=json.dumps({"error": "API key not configured"}),
                status_code=500,
                mimetype="application/json"
            )
        
        cur_CI, cur_zone, timestamp = get_cur_CI(EM_KEY)
        
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching carbon intensity: {str(e)}")

        return func.HttpResponse(
            body=json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            mimetype="application/json"
        )


    # Create table row 
    data = {
        "PartitionKey": "pending", # Effectively table name
        "RowKey": str(uuid.uuid4()), # Generates a key 
        "Prompt": prompt_text,      
        #"Timestamp":  datetime.now().isoformat(),
        "Model": model,
        "Schedule": schedule,
        "CarbonIntensity_s": cur_CI,
        "CarbonIntensity_c": 0
    }


    table_json = json.dumps(data)
    message.set(table_json)

    return func.HttpResponse(
        body=json.dumps({"message": f"Scheduled successfully.","status": "ok"}),
        status_code=200,
        mimetype="application/json"
    )

@app.function_name(name="GetPrompts")
@app.route(route="prompts", methods=["GET"])
@app.table_input(arg_name="prompts",
                 connection="TABLE_PROMPT_STORAGE",
                 table_name="prompttable")
def get_prompts(req: func.HttpRequest, prompts) -> func.HttpResponse:
    try:
        # Parse json string 
        prompts_data = json.loads(prompts)
        
        prompts_list = []
        for prompt in prompts_data:
            prompts_list.append({
                "id": prompt['RowKey'],
                "prompt": prompt['Prompt'],
                "carbonIntensity_S": prompt['CarbonIntensity_s'],
                "carbonIntensity_C": prompt['CarbonIntensity_c'],
                "status": prompt['PartitionKey'],
                "model": prompt['Model'],
                "schedule": prompt['Schedule']
            })
        
        return func.HttpResponse(
            body=json.dumps(prompts_list),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(
            body=json.dumps({"error": prompts_list}),
            status_code=500,
            mimetype="application/json"
        )
    
@app.function_name(name="GetCarbonIntensityPast")
@app.route(route="carbon-intensity-past", auth_level=func.AuthLevel.ANONYMOUS)
def get_CI_past(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching carbon intensity data.')

    try:
        EM_KEY = os.environ.get("ELECTRICITY_MAPS_API_KEY")

        if not EM_KEY:
            return func.HttpResponse(
                body=json.dumps({"error": "API key not configured"}),
                status_code=500,
                mimetype="application/json"
            )

        url =  "https://api.electricitymaps.com/v3/carbon-intensity/history?dataCenterRegion=eastus2&dataCenterProvider=azure&disableEstimations=true&emissionFactorType=direct"
        headers={"auth-token": EM_KEY}
        response = requests.get(url,headers=headers)
        response.raise_for_status()

        intensities = [item['carbonIntensity'] for item in response.json()['history']]
        stamps = [item['datetime'] for item in response.json()['history']]
        simple_stamps = [
            datetime.fromisoformat(ts).astimezone(ZoneInfo("America/Denver")).strftime("%b %d %H:%M")
            for ts in stamps
        ]
                
        payload = {
            "intensities": intensities,
            "stamps": simple_stamps,
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
    