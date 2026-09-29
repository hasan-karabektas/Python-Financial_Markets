import requests
import pandas as pd


def get_nasdaq100_tickers():

    URL = "https://indexes.nasdaq.com/Index/Breakdown/NDX"

    headers = {
        "User-Agent": "MyMarketBot/1.0"
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    tables = pd.read_html(response.text)

    for table in tables:

        table.columns = [
            str(col).strip()
            for col in table.columns
        ]

        symbol_columns = [
            col for col in table.columns
            if str(col).upper() == "SYMBOL"
        ]

        if symbol_columns:

            df = table.copy()
            df = df.rename(
                columns={symbol_columns[0]: "Ticker"}
            )

            df["Ticker"] = (
                df["Ticker"]
                .astype(str)
                .str.strip()
                .str.replace(".", "-", regex=False)
            )

            # Basic sanity check
            if len(df) < 90:
                raise ValueError(
                    f"Nasdaq returned only {len(df)} constituents. "
                    "The page structure may have changed."
                )

            return df

    raise ValueError(
        "Could not find Nasdaq-100 constituent table."
    )
