import requests
import pandas as pd
from io import StringIO


def get_nasdaq100_tickers():

    URL = "https://www.nasdaq.com/NDX"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))

    for table in tables:

        table.columns = [
            str(col).strip()
            for col in table.columns
        ]

        if "Symbol" in table.columns:

            df = table.copy()

            df = df.rename(columns={
                "Symbol": "Ticker"
            })

            df["Ticker"] = (
                df["Ticker"]
                .astype(str)
                .str.strip()
                .str.replace(".", "-", regex=False)
            )

            if len(df) < 90:
                raise ValueError(
                    f"Nasdaq NDX returned only {len(df)} constituents."
                )

            return df

    raise ValueError(
        "Nasdaq NDX constituent table not found."
    )
