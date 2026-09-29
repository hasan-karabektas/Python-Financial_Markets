import requests
import pandas as pd


def get_nasdaq100_tickers():

    url = "https://api.nasdaq.com/api/quote/NDX/holdings"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nasdaq.com/",
        "Origin": "https://www.nasdaq.com",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    # Check the API response
    if not data.get("data"):
        raise ValueError(
            f"Unexpected Nasdaq API response: {data}"
        )

    rows = data["data"].get("rows", [])

    if not rows:
        raise ValueError(
            "Nasdaq API returned no NDX constituents."
        )

    df = pd.DataFrame(rows)

    # Find the ticker column
    ticker_column = None

    for col in df.columns:
        if col.lower() in {
            "symbol",
            "symbols",
            "ticker",
            "securitysymbol"
        }:
            ticker_column = col
            break

    if ticker_column is None:
        raise ValueError(
            f"Could not identify ticker column. "
            f"Columns returned: {list(df.columns)}"
        )

    df = df.rename(columns={ticker_column: "Ticker"})

    df["Ticker"] = (
        df["Ticker"]
        .astype(str)
        .str.strip()
        .str.replace(".", "-", regex=False)
    )

    # Sanity check
    if len(df) < 90:
        raise ValueError(
            f"Nasdaq API returned only {len(df)} constituents."
        )

    return df
