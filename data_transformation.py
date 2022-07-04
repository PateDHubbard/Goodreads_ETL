import pandas as pd


def transform_data(raw_data_path, books_exclude_path):
    df = pd.read_csv(raw_data_path)
    df_exclude = pd.read_csv(books_exclude_path)

    books = df.drop([
       "Author l-f", "Bookshelves", "Bookshelves with positions",
       "Recommended For", "Recommended By", "Owned Copies",
       "Original Purchase Date", "Original Purchase Location", "Condition",
       "Condition Description", "BCID"
       ], axis=1).copy()
    books["ISBN"] = books["ISBN13"].str.replace('[",=]', '')
    books["ISBN13"] = books["ISBN13"].str.replace('[",=]', '')
    books.drop_duplicates(subset=["Title"], inplace=True)
    books.set_index("Book Id", inplace=True)

    books_to_exclude = df_exclude.drop(columns="Title").set_index("Book Id")
    books = books.join(books_to_exclude, on="Book Id")
    books.reset_index(inplace=True)

    shelves_raw = df[["Book Id", "Bookshelves"]].copy()
    shelves_raw = pd.concat([
        shelves_raw[["Book Id"]],
        shelves_raw["Bookshelves"].str.split(', ', expand=True)
        ], axis=1)
    shelves_pivoted = pd.melt(
        shelves_raw, id_vars=["Book Id"],
        value_name="Shelf"
        ).drop(["variable"], axis=1)
    shelves = shelves_pivoted.dropna()

    books.to_csv("books.csv", index=False)
    shelves.to_csv("shelves.csv", index=False)
