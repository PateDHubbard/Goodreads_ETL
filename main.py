import os
import json

from selenium_scrape import create_driver, log_in_goodreads, download_export
from data_transformation import transform_data
from google_drive import get_google_drive, add_file_to_drive, download_file
from db_logging import save_logs, add_to_logs

logs = []

try:
    with open("my_credentials.json") as file:
        my_credentials = json.load(file)

    cwd = os.getcwd()
    USERNAME = my_credentials["Username"]
    PASSWORD = my_credentials["Password"]

    FOLDER_ID = "1Qit_4HKiP0NT3JvBWPu7XG38jSz8X9n0"
    FILES_TO_UPLOAD = ["books.csv", "shelves.csv"]

    FILES_TO_DELETE = FILES_TO_UPLOAD + [
        "goodreads_library_export.csv", "books_to_exclude.csv"
        ]
    add_to_logs(logs, "Process Initialization", "Success")
except Exception as e:
    add_to_logs(logs, "Process Initialization", "Failure", str(e))
    save_logs(logs)
    print(e)
    exit()


try:
    driver = create_driver(download_path=cwd)
    log_in_goodreads(driver, USERNAME, PASSWORD)
    ###
    add_to_logs(logs, "Log Into Goodreads", "Success")
    print("Successfully logged into Goodreads")
except Exception as e:
    add_to_logs(logs, "Log Into Goodreads", "Failure", str(e))
    save_logs(logs)
    print(str(e))
    exit()

try:
    download_export(driver, cwd)
    driver.close()
    ###
    add_to_logs(logs, "Download Goodreads Export", "Success")
    print("Successfully downloaded Goodreads export")
except Exception as e:
    add_to_logs(logs, "Download Goodreads Export", "Failure", str(e))
    save_logs(logs)
    print(str(e))
    exit()


try:
    drive = get_google_drive()
    download_file(drive, FOLDER_ID, "books_to_exclude.csv")
    raw_data_path = os.path.join(cwd, "goodreads_library_export.csv")
    transform_data(
        raw_data_path=raw_data_path,
        books_exclude_path="books_to_exclude.csv"
        )
    ####
    add_to_logs(logs, "Transform Data", "Success")
    print("Completed data transformation")
except Exception as e:
    add_to_logs(logs, "Transform Data", "Failure", str(e))
    save_logs(logs)
    print(str(e))
    exit()


try:
    for file in FILES_TO_UPLOAD:
        add_file_to_drive(drive, file, FOLDER_ID)
        print(f"Successfully added {file} to drive")
    for file in FILES_TO_DELETE:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass
    ###
    print("Succesfully uploaded final data to drive")
    add_to_logs(logs, "Upload Data to Drive", "Success")
except Exception as e:
    add_to_logs(logs, "Upload Data to Drive", "Failure", str(e))
    save_logs(logs)
    print(str(e))
    exit()
    
save_logs(logs)
