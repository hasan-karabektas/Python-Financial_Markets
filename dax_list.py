import requests
import pandas as pd
from io import StringIO

def get_dax_tickers():
    API_URL = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": "DAX", 
        "format": "json",
        "prop": "text",
        "formatversion": 2
    }
    headers = {"User-Agent": "MyMarketBot/1.0"}

    response = requests.get(API_URL, params=params, headers=headers)
    html = response.json()["parse"]["text"]
    tables = pd.read_html(StringIO(html))

    df = None
    for table in tables:
        if "Ticker" in table.columns or "Symbol" in table.columns:
            if len(table) >= 30:   
                df = table.copy()
                break

    df["Ticker"] = df["Ticker"].str.replace(r"\[.*\]", "", regex=True)
    df["Ticker"] = df["Ticker"].str.strip()
    df["Ticker"] = df["Ticker"].apply(lambda x: x if "." in x else x + ".DE")
    
    return df

