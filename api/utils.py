import requests
from openai import AzureOpenAI
from datetime import datetime, timezone, timedelta

def get_cur_CI(EM_KEY):
    url = "https://api.electricitymaps.com/v3/carbon-intensity/latest?dataCenterRegion=eastus2&dataCenterProvider=azure&disableEstimations=true&emissionFactorType=direct"
    headers={"auth-token": EM_KEY}
    response = requests.get(url,headers=headers)
    response.raise_for_status()

    cur_CI = response.json()["carbonIntensity"]
    cur_zone = response.json()["zone"]
    timestamp = response.json()["datetime"]

    return cur_CI, cur_zone, timestamp

def get_cuttoff(schedule):
    match schedule:
        case "6 hr":
            return (datetime.now() + timedelta(hours=6)).isoformat()
        case "12 hr":
            return (datetime.now() + timedelta(hours=12)).isoformat()
        case "24 hr":
            return (datetime.now() + timedelta(hours=24)).isoformat()
        case "48 hr":
            return (datetime.now() + timedelta(hours=48)).isoformat()
