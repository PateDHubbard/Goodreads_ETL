import requests
import uuid


# Log group is set just once for the entire session
LOG_GROUP = str(uuid.uuid1())
URL = "https://king-prawn-app-ebwri.ondigitalocean.app/logging/goodreads_etl"


def send_log_to_db(log_name, log_status, log_notes=None):
    data = {
        "log_group": LOG_GROUP,
        "log_name": log_name,
        "log_status": log_status,
        "log_notes": log_notes
    }
    response = requests.post(URL, data=data)
    return response
