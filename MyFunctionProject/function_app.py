import azure.functions as func
import datetime
import json
import logging
import csv
import codecs
import os
import io
from azure.storage.blob import BlobServiceClient
from additional_functions import bp


def process_csv(blob_content):
    summary = {"processed": 0, "errors": 0}
    
    try:
        # Try to decode CSV content safely
        decoded_content = blob_content.decode('utf-8-sig', errors='replace')
        reader = csv.DictReader(io.StringIO(decoded_content))
        
        # Check for headers
        if not reader.fieldnames:
            raise csv.Error("Missing headers in CSV file.")
        
        for row in reader:
            try:
                # Your row processing logic here
                # Example: print(row)
                summary["processed"] += 1
            except Exception as e:
                summary["errors"] += 1
                logging.error(f"Row processing error: {e}")
                
    except (csv.Error, UnicodeDecodeError) as e:
        summary["errors"] += 1
        logging.error(f"Failed to read CSV: {e}")
    except Exception as e:
        summary["errors"] += 1
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info(f"CSV Summary: {summary}")
        
    return summary
