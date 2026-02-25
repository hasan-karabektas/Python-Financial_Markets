import requests
import pandas as pd
from io import StringIO

def get_nasdaq100_tickers():
    API_URL = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "parse",
        "page": "Nasdaq-100",
        "format": "json",
        "prop": "text",
        "formatversion": 2
    }

    headers = {
        "User-Agent": "MyMarketBot/1.0"
    }

    response = requests.get(API_URL, params=params, headers=headers)
    response.raise_for_status()

    html = response.json()["parse"]["text"]
    tables = pd.read_html(StringIO(html))

    df = None
    for table in tables:
        if "Ticker" in table.columns:
            df = table
            break

    if df is None:
        raise ValueError("Nasdaq-100 constituents table not found.")

    df["Ticker"] = df["Ticker"].str.replace(".", "-", regex=False)

    return df


