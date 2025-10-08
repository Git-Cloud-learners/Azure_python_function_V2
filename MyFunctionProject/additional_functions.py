import logging
import azure.functions as func

def main(myblob: func.InputStream):
    logging.info(f"Processing blob: Name={myblob.name}, Size={myblob.length} bytes")

    blob_bytes = myblob.read()
    summary = process_csv(blob_bytes)

    logging.info(f"Processing completed. Summary: {summary}")