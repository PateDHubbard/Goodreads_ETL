from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os
import time


def set_chrome_options(download_path):
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {"download.default_directory": download_path}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


def create_driver(download_path):
    chrome_options = set_chrome_options(download_path)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def log_in_goodreads(driver, username, password):
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
    driver.find_element(By.ID, "ap_email").send_keys(username)
    driver.find_element(By.ID, "ap_password").send_keys(password)
    driver.find_element(By.ID, "signInSubmit").click()


def download_export(driver, download_path):
    driver.get("https://www.goodreads.com/review/import")
    driver.find_element(By.CLASS_NAME, "js-LibraryExport").click()

    csv_path = os.path.join(download_path, "goodreads_library_export.csv")
    if os.path.exists(csv_path):
        os.remove(csv_path)

    flag = True
    counter = 0
    while flag:
        time.sleep(5)
        try:
            driver.find_element(By.CSS_SELECTOR, "#exportFile > a").click()
            if os.path.exists(csv_path):
                flag = False
        except NoSuchElementException:
            print("Waiting...")
            counter += 1
            if counter > 75:
                raise Exception("Waiting for export button time out.")
