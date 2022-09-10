from boto3 import session
from botocore.client import Config
import datetime as dt
import json
import uuid
import os

# Log group is set just once for the entire session
LOG_GROUP = str(uuid.uuid1())

SESSION = session
ACCESS_ID = 'DO00M4Z4X8UH3GMFDT44'
SECRET_KEY = 'Hx/cb9dcsluRa7cE3iehjwKqQ9gl4IJCgAPulASsPsM'


def send_log_to_db(log_name, log_status, log_notes=None):
    # Initiate session
    session = SESSION.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            aws_access_key_id=ACCESS_ID,
                            aws_secret_access_key=SECRET_KEY)

    data = {
        "log_group": LOG_GROUP,
        "log_name": log_name,
        "log_status": log_status,
        "log_notes": log_notes
    }
    now = dt.datetime.strftime(dt.datetime.now(), "%Y_%m_%d_%H_%M_%S")
    file_name = "log_" + now + ".json"
    with open(file_name, 'w') as file:
        json.dump(data, file)

    try:
        client.upload_file(file_name, "pate-object-storage", "goodreads_etl_logs/" + file_name)
        os.remove(file_name)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    send_log_to_db("patricia", "success", "notes")
