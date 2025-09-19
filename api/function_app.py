import azure.functions as func
import logging
import json

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
