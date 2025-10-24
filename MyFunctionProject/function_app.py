import azure.functions as func
import datetime
import json
import logging
import csv
import codecs
import os
from azure.storage.blob import BlobServiceClient
from additional_functions import bp

app = func.FunctionApp()

app.register_blueprint(bp) 

@app.function_name('FirstHTTPFunction')
@app.route(route="myroute", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    return func.HttpResponse(
        "Wow this first HTTP Function works!!!!",
        status_code=200
    )

@app.function_name('SecondHTTPFunction')
@app.route(route="newroute")
def second_http_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting the second HTTP Function request.')
   
    name = req.params.get('name', "")

    # Input validation
    if not name:
        error = {"error": "Name cannot be empty"}
        return func.HttpResponse(
            json.dumps(error),
            status_code=400,
            mimetype="application/json"
        )
    if len(name) > 50:
        error = {"error": "Name cannot exceed 50 characters"}
        return func.HttpResponse(
            json.dumps(error),
            status_code=400,
            mimetype="application/json"
        )
    if not name.isalnum():
        error = {"error": "Name must be alphanumeric"}
        return func.HttpResponse(
            json.dumps(error),
            status_code=400,
            mimetype="application/json"
        )

    # If validation passes
    message = {"message": f"Hello, {name}, so glad this Function worked!!"}
    return func.HttpResponse(
        json.dumps(message),
        status_code=200,
        mimetype="application/json"
    )


@app.function_name(name="MyFirstBlobFunction")
@app.blob_trigger(arg_name="myblob", 
                  path="newcontainer/People.csv",
                  connection="AzureWebJobsStorage")
def test_function(myblob: func.InputStream):
   logging.info(f"Python blob Function triggered after the People.csv file was uploaded to the newcontainer. So cool!!!! \n"
                f"Printing the name of the blob path: {myblob.name}"
                )
   blob_name = myblob.name.split('/')[-1]
   metadata_log = f"Blob: {blob_name}, Size: {myblob.length} bytes, Last Modified: {myblob.last_modified}"
   logging.info(metadata_log)
   
   # Optional: Append metadata to log file in blob storage
   try:
       # Get connection string from app settings
       connection_string = os.environ.get('AzureWebJobsStorage')
       if connection_string:
           # Create a BlobServiceClient
           blob_service_client = BlobServiceClient.from_connection_string(connection_string)
           # Get container client
           container_client = blob_service_client.get_container_client("newcontainer")
           
           # Get the metadata log blob client
           log_blob_name = "metadata.log"
           blob_client = container_client.get_blob_client(log_blob_name)
           
           # Check if the log file exists, if not create it
           try:
               # Try to download the existing log
               existing_log = blob_client.download_blob().readall().decode('utf-8')
               log_content = existing_log + "\n" + metadata_log
           except Exception:
               # Log file doesn't exist yet, create new log content
               log_content = metadata_log
           
           # Upload the updated log
           blob_client.upload_blob(log_content, overwrite=True)
           logging.info(f"Metadata appended to {log_blob_name}")
   except Exception as e:
       logging.error(f"Error appending to metadata log: {str(e)}")
   

@app.function_name(name="ReadFileBlobFunction")
@app.blob_trigger(arg_name="readfile",
                  path="newcontainer/People2.csv",
                  connection="AzureWebJobsStorage")
def main(readfile: func.InputStream):
    reader=csv.reader(codecs.iterdecode(readfile,'utf-8'))
    for line in reader:
        print(line)
