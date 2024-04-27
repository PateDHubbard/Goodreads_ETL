import os

from goodreads import GoodreadsETL
from google_drive import get_google_drive, add_file_to_drive

METHOD = "manual" # options are 'manual' and 'selenium'
goodreads_etl = GoodreadsETL()

if METHOD == "manual":
    soup = goodreads_etl.create_soup_from_html("my_export.html")
elif METHOD == "selenium":
    soup = goodreads_etl.create_soup_using_selenium()

df = goodreads_etl.parse_soup_to_df(soup)
goodreads_etl.create_books_csv(df)
goodreads_etl.create_shelves_csv(df)
goodreads_etl.create_dates_read_csv(df)

drive = get_google_drive()
for file in ["books.csv", "shelves.csv", "dates_read.csv"]:
    add_file_to_drive(drive, file, "1Qit_4HKiP0NT3JvBWPu7XG38jSz8X9n0")
    os.remove(file)
