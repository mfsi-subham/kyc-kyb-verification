import logging
import requests
import time
import azure.functions as func
import json
import os
from azure.storage.blob import BlobServiceClient


def main(event: func.EventGridEvent):
    # storing event result
    result = {"data": event.get_json()}
    # Endpoint of the azure ocr
    endpoint = os.environ["OCR_ENDPOINT"]
    # subscription key of azure ocr
    subscription_key = os.environ["OCR_SUBSCRIPTION_KEY"]
    # url for READ API service of azure cognitive service
    text_recognition_url = endpoint + "/vision/v3.0/read/analyze"
    # uploaded url of image
    image_url = result["data"]["url"]
    
    # passing subscription key in header
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    data = {"url": image_url}
    response = requests.post(text_recognition_url, headers=headers, json=data)
    response.raise_for_status()

    # analyze the data from response
    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
        time.sleep(1)
        if ("analyzeResult" in analysis):
            poll = False
        if ("status" in analysis and analysis["status"] == "failed"):
            poll = False

    if ("analyzeResult" in analysis):
        
        json_file_name = image_url.split("/")[4].split(".")[0] +".json"
        # Storing data in azure-blob
        data =  json.dumps(analysis, indent=4)
        connect_str = os.environ["JSON_BLOB_CONNECTION_STRING"]
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(
                        container="kyc-kyb-json",
                        blob=json_file_name
                    )
        
        blob_client.upload_blob(data, overwrite=True)
        
    