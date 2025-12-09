import azure.functions as func
import datetime
import json
import logging
import os
from dotenv import load_dotenv

app = func.FunctionApp()

load_dotenv()


@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS)
def hello(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    KEY = os.getenv("MY_KEY")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if name:
        return func.HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully."
        )
    else:
        return func.HttpResponse(
            f"This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response. My key is {KEY}",
            status_code=200,
        )
