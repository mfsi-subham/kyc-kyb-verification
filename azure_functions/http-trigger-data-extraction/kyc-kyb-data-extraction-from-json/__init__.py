import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import json
import os


def main(req: func.HttpRequest) -> func.HttpResponse:
    # get json file from query parameter
    json_file_name = req.params.get('json_file_name')

    # connections to the azure blob to get data from json file
    azure_connection_string = os.environ["JSON_BLOB_CONNECTION_STRING"]
    blob_service_client = BlobServiceClient.from_connection_string(
                                    azure_connection_string
                                )
    blob_client = blob_service_client.get_blob_client(
                                                    container="kyc-kyb-json",
                                                    blob=json_file_name
                                                )
    # convert the data to json format
    data = json.loads(blob_client.download_blob().readall().decode("utf-8"))
    results = data["analyzeResult"]["readResults"][0]

    # extracting useful infos
    country = results["lines"][0]["words"][-1]["text"]
    passport_no = results["lines"][7]["text"]
    surname = results["lines"][8]["text"]
    firstname = results["lines"][10]["text"]
    sex = results["lines"][15]["text"]
    dob = results["lines"][16]["text"]
    place_of_birth = results["lines"][18]["text"]
    place_of_issue = results["lines"][20]["text"]
    date_of_issue = results["lines"][23]["text"]
    date_of_expiry = results["lines"][24]["text"]

    # create a dict to send it to HTTPResponse
    final_output = {
        "country": country,
        "passport_no" : passport_no,
        "surname": surname,
        "firstname": firstname,
        "sex": sex,
        "dob": dob,
        "place_of_birth": place_of_birth,
        "place_of_issue": place_of_issue,
        "date_of_issue": date_of_issue,
        "date_of_expiry": date_of_expiry
    }

    # checking for request body in json file_name is not found in json query
    if not json_file_name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            json_file_name = req_body.get('json_file_name')


    if json_file_name:
        return func.HttpResponse(
            json.dumps(final_output),
            mimetype="application/json",
        )
    else:
        return func.HttpResponse(
             "Please pass a json_file_name on the query string",
             status_code=400
        )
