import requests
import pandas as pd
from io import StringIO

def get_euronext100_tickers():
    API_URL = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "parse",
        "page": "Euronext 100",
        "format": "json",
        "prop": "text",
        "formatversion": 2
    }

    headers = {"User-Agent": "MyMarketBot/1.0"}

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
        raise ValueError("Euronext 100 table not found.")


    df["Ticker"] = df["Ticker"].str.strip()

    return df[["Ticker", "Name"]]

try:
    en100 = get_euronext100_tickers()

except Exception as e:
    print(f"Error: {e}")


