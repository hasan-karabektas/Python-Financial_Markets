import requests
import pandas as pd
from io import StringIO


def get_nasdaq100_tickers():

    URL = "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies"

    headers = {
        "User-Agent": "MyMarketBot/1.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))

    for table in tables:

        # Clean column names
        table.columns = [
            str(col).strip()
            for col in table.columns
        ]

        if "Ticker" in table.columns:

            df = table.copy()

            # Clean ticker symbols
            df["Ticker"] = (
                df["Ticker"]
                .astype(str)
                .str.strip()
                .str.replace(".", "-", regex=False)
            )

            return df

    raise ValueError(
        "Nasdaq-100 constituents table not found. "
        f"Tables found: {[list(t.columns) for t in tables]}"
    )
