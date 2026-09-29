import requests
import pandas as pd
from io import StringIO

def get_nasdaq100_tickers():

    API_URL = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "parse",
        "page": "Nasdaq-100",
        "prop": "text",
        "format": "json",
        "formatversion": "2"
    }

    headers = {
        "User-Agent": "MyMarketBot/1.0 (contact@example.com)"
    }

    with requests.Session() as session:

        response = session.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

    # Check that the expected API response exists
    if "parse" not in data:
        raise ValueError(f"Unexpected Wikipedia API response: {data}")

    html = data["parse"]["text"]

    tables = pd.read_html(StringIO(html))

    # Find the Nasdaq-100 constituents table
    df = None

    for table in tables:
        # Normalize column names
        table.columns = [
            str(col).strip()
            for col in table.columns
        ]

        if "Ticker" in table.columns:
            df = table.copy()
            break

    if df is None:
        raise ValueError(
            "Nasdaq-100 constituents table not found. "
            f"Available columns: {[list(t.columns) for t in tables]}"
        )

    # Clean ticker column
    df["Ticker"] = (
        df["Ticker"]
        .astype(str)
        .str.strip()
        .str.replace(".", "-", regex=False)
    )

    return df
