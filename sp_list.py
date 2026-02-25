import requests
import pandas as pd
from io import StringIO

def get_sp500_tickers():
    API_URL = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "parse",
        "page": "List of S&P 500 companies",
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
    df = tables[0]

    df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)

    return df




