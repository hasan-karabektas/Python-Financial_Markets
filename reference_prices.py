import pandas as pd
from datetime import datetime, timedelta

def build_reference_df(data, tickers):

    today = datetime.today()
    reference_dict = {}

    for ticker in tickers:
        try:
            series = data[ticker]["Adj Close"].dropna()

            if len(series) < 10:
                continue

            # Previous close
            prev_close = series.iloc[-2]
            prev_close_date = series.index[-2]

            # Target dates
            target_1y = today - timedelta(days=365)
            target_1m = today - timedelta(days=30)
            target_1w = today - timedelta(days=7)

            # Find closest previous trading day
            year_price = series[series.index <= target_1y].iloc[-1]
            month_price = series[series.index <= target_1m].iloc[-1]
            week_price = series[series.index <= target_1w].iloc[-1]

            reference_dict[ticker] = {
                "1Y_Ago": year_price,
                "1M_Ago": month_price,
                "1W_Ago": week_price,
                "Prev_Close": prev_close,
                "Prev_Close_Date": prev_close_date
            }

        except Exception:
            continue

    return pd.DataFrame.from_dict(reference_dict, orient="index")


