# Goodreads Personal Library ETL

This project automates the process for downloading and transforming my personal book reading information from Goodreads for use in my [Goodreads Personal Library Overview](https://public.tableau.com/app/profile/payton1178/viz/GoodreadsPersonalLibraryOverview/Overview) Tableau dashboard.

### Overview
This process has 3 main steps:
1. The app uses the Selenium browser automation library to download the CSV of book information from the Goodreads website. Most of this logic is contained in the `selenium_scrape.py` file.
2. The downloaded CSV is transformed into 2 separate CSVs to form a very basic, 2 table data model. The transformation logic is contained in the `data_transformation.py` file.
3. The new cleaned and transformed CSVs are uploaded to my personal Google Drive where they overwrite the old files. This logic is contained in the `google_drive.py` file. 

### Installation & Usage
The project can be run locally by simply cloning the repo and installing the requirements using pip.

```
pip install requirements.txt
```

The user needs to provide Google Drive Oauth credentials in a `client_secrets.json` file along according to the directions in [PyDrive's documentation](https://pythonhosted.org/PyDrive/quickstart.html#authentication). 

The project also requires the user's Goodreads email and password to download the book data. This should be provided in a `my_credentials.json` file with the following format:
```json
{
    "Username": "<goodreads_username>",
    "Password": "<goodreads_password>"
}
```

After installing the requirements and providing the credentials files, the process can be triggered by running:
```
python main.py
```

A Dockerfile is also provided for creating a Docker image for easy deployment.