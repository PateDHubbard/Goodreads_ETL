import datetime as dt
import json
import time
import os
import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

from google_drive import get_google_drive, add_file_to_drive

with open('my_credentials.json') as file:
    credentials = json.load(file)

download_path = "/"

# Sets chrome options for Selenium. Chrome options for headless browser is enabled.
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_prefs = {"download.default_directory": download_path}
chrome_options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}

# create driver
driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.goodreads.com/")
driver.find_element(By.LINK_TEXT, "Sign In").click()
driver.find_element(
    By.CSS_SELECTOR,
    ".gr-button."
    "gr-button--dark"
    ".gr-button--auth."
    "authPortalConnectButton"
    ".authPortalSignInButton"
    ).click()
driver.find_element(By.ID, "ap_email").send_keys(credentials["username"])
driver.find_element(By.ID, "ap_password").send_keys(credentials["password"])
driver.find_element(By.ID, "signInSubmit").click()
driver.get("https://www.goodreads.com/")

driver.get("https://www.goodreads.com/review/list/43561162?ref=nav_mybooks")
for i in range(1, 20):
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)


page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
books_table = soup.find("table", {"id": "books"})
rows_clean = {
    "title": [],
    "author": [],
    "isbn": [],
    "isbn13": [],
    "num_pages": [],
    "avg_rating": [],
    "num_ratings": [],
    "date_published": [],
    "rating": [],
    "shelves": [],
    "num_times_read": [],
    "date_started": [],
    "date_read": [],
    "date_added": []
}
rows_raw = books_table.find_all("tr")[1:]
for row in rows_raw:
    rows_clean["title"].append(re.sub(" +|title|\n", " ", row.find_all("td")[3].text).strip())
    rows_clean["author"].append(re.sub(" +|author|\n|\\*", " ", row.find_all("td")[4].text).strip())
    rows_clean["isbn"].append(re.sub(" +|isbn|\n", " ", row.find_all("td")[5].text).strip())
    rows_clean["isbn13"].append(re.sub(" +|isbn13|\n", " ", row.find_all("td")[6].text).strip())
    rows_clean["num_pages"].append(re.sub(" +|num pages|\n|pp|,", " ", row.find_all("td")[8].text).strip())
    rows_clean["avg_rating"].append(re.sub(" +|avg rating|\n", " ", row.find_all("td")[9].text).strip())
    rows_clean["num_ratings"].append(re.sub(" +|num ratings|\n|,", "", row.find_all("td")[10].text).strip())
    rows_clean["date_published"].append(re.sub(" +|date pub|\n", " ", row.find_all("td")[11].text).strip())
    rows_clean["rating"].append(re.search('\[(.*?)\]|$', row.find_all("td")[13].text)[0].strip())
    rows_clean["shelves"].append(re.sub(" +|shelves|\n|\[edit\]", " ", row.find_all("td")[14].text).strip())
    rows_clean["num_times_read"].append(re.sub(" +|\# times read|\n", " ", row.find_all("td")[19].text).strip())
    rows_clean["date_started"].append(re.sub(" +|date started|\n|\[edit\]", " ", row.find_all("td")[20].text).strip())
    rows_clean["date_read"].append(re.sub(" +|date read|\n", " ", row.find_all("td")[21].text).replace("[edit]", ";").strip()[:-1])
    rows_clean["date_added"].append(re.sub(" +|date added|\n", " ", row.find_all("td")[22].text).strip())


df = pd.DataFrame(rows_clean)

df["rating"] = df["rating"].str.replace("[", '').str.replace("]", "").str.strip().str[0]
df.reset_index(inplace=True)

def extract_shelf(x):
    if "to-read" in x:
        return "to-read"
    elif "currently-reading" in x:
        return "currently-reading"
    else:
        return 'read'

df["exclusive_shelf"] = df['shelves'].apply(extract_shelf)

shelves_raw = df[["index", "shelves"]].copy()
shelves_raw = pd.concat([
    shelves_raw[["index"]],
    shelves_raw["shelves"].str.split(', ', expand=True)
    ], axis=1)
shelves_pivoted = pd.melt(
    shelves_raw, id_vars=["index"],
    value_name="shelf"
    ).drop(["variable"], axis=1)
shelves = shelves_pivoted.dropna()

dates_read_raw = df[["index", "date_read"]].copy()
dates_read_raw = pd.concat([
    dates_read_raw[["index"]],
    dates_read_raw["date_read"].str.split('; ', expand=True)
    ], axis=1)
dates_read_pivoted = pd.melt(
    dates_read_raw, id_vars=["index"],
    value_name="date_read"
    ).drop(["variable"], axis=1)
dates_read = dates_read_pivoted.dropna()
dates_read["date_read"] = dates_read["date_read"].str.strip()

def convert_dates(x):
    if x == "not set":
        return None
    elif "," in x:
        date_time = dt.datetime.strptime(x, "%b %d, %Y")
    else:
        date_time = dt.datetime.strptime(x, "%b %Y")
    return date_time.strftime("%Y-%m-%d")

dates_read["date_read"] = dates_read["date_read"].apply(convert_dates)


df.to_csv("books.csv", index=False)
shelves.to_csv("shelves.csv", index=False)
dates_read.to_csv("dates_read.csv", index=False)

FOLDER_ID = "1Qit_4HKiP0NT3JvBWPu7XG38jSz8X9n0"
FILES_TO_UPLOAD = ["books.csv", "shelves.csv", "dates_read.csv"]

drive = get_google_drive()
for file in FILES_TO_UPLOAD:
    add_file_to_drive(drive, file, FOLDER_ID)

for file in FILES_TO_UPLOAD:
    try:
        os.remove(file)
    except FileNotFoundError:
        pass

