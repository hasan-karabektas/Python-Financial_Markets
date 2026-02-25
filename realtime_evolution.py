import yfinance as yf
import pandas as pd

def compute_realtime_evolution(tickers, reference_df):

    tickers = reference_df.index.tolist()

    print(f"Fetching live prices for {len(tickers)} tickers...")

    live_prices = {}
    names = {}
    industries = {}
    sectors = {}

    live_data = yf.download(
    tickers,
    period="1d",
    group_by="ticker",
    threads=True,
    progress=False
    )

    live_prices = {}

    for t in tickers:
        try:
            if len(tickers) == 1:
                live_prices[t] = live_data["Close"].iloc[-1]
            else:
                live_prices[t] = live_data[t]["Close"].iloc[-1]

            info = yf.Ticker(t).info
            names[t] = info.get("longName")
            industries[t] = info.get("industry")
            sectors[t] = info.get("sector")

        except:
            live_prices[t] = None
            names[t] = None
            industries[t] = None
            sectors[t] = None


    live_df = pd.DataFrame.from_dict(live_prices, orient="index", columns=["Live_Price"])
    live_df["Name"] = pd.Series(names)
    live_df["Industry"] = pd.Series(industries)
    live_df["Sector"] = pd.Series(sectors)
    live_df.index.name = "Ticker"

    df = reference_df.join(live_df)
    df["Prev_Close_Date"] = pd.to_datetime(df["Prev_Close_Date"]).dt.date

    
    df["%_vs_Prev_Close"] = (df["Live_Price"] / df["Prev_Close"] - 1) * 100
    df["%_vs_1W_Ago"] = (df["Live_Price"] / df["1W_Ago"] - 1) * 100
    df["%_vs_1M_Ago"] = (df["Live_Price"] / df["1M_Ago"] - 1) * 100
    df["%_vs_1Y_Ago"] = (df["Live_Price"] / df["1Y_Ago"] - 1) * 100

    numeric_cols = df.select_dtypes(include=["float64", "float32"]).columns
    df[numeric_cols] = df[numeric_cols].round(2)
    return df


def rank_performers(df):

    sorted_df = df.sort_values(by="%_vs_Prev_Close")

    worst = sorted_df.head(10)

    top = sorted_df.tail(10).sort_values(by="%_vs_Prev_Close", ascending=False)

    return top, worst

def build_index_evolution(tickers, period="2y"):

    from get_yf_historical_data import download_daily_data
    from reference_prices import build_reference_df

    data = download_daily_data(tickers, period=period)


    valid_tickers = []

    for t in tickers:
        try:
            ticker_close = data[t]["Close"].dropna()
            if not ticker_close.empty:
                valid_tickers.append(t)
            else:
                print(f"Removing invalid ticker (no data): {t}")
        except Exception:
            print(f"Removing invalid ticker (error): {t}")

    if valid_tickers:
        data = data.loc[:, data.columns.get_level_values(0).isin(valid_tickers)]

    tickers = valid_tickers

    reference = build_reference_df(data, tickers)

    df = compute_realtime_evolution(tickers, reference)

    top, worst = rank_performers(df)

    return top, worst

if __name__ == "__main__":
    from sp_list import get_sp500_tickers
    from nasdaq_list import get_nasdaq100_tickers
    from dax_list import get_dax_tickers
    from euronext_list import get_euronext100_tickers
    from get_yf_historical_data import download_daily_data
    from reference_prices import build_reference_df

    sp500_df = get_sp500_tickers()
    nasdaq_df = get_nasdaq100_tickers()
    dax_df = get_dax_tickers()
    euro_df = get_euronext100_tickers()

    sp_tickers = sp500_df["Symbol"].tolist()
    nq_tickers = nasdaq_df["Ticker"].tolist()
    dax_tickers = dax_df["Ticker"].tolist()
    euro_tickers = euro_df["Ticker"].tolist()

    print(f"S&P 500 tickers: {len(sp_tickers)}")
    print(f"Nasdaq-100 tickers: {len(nq_tickers)}")
    print(f"DAX tickers: {len(dax_tickers)}")
    print(f"Euronext 100 tickers: {len(euro_tickers)}")

    sp_data = download_daily_data(sp_tickers, period="2y")
    nq_data = download_daily_data(nq_tickers, period="2y")
    dax_data = download_daily_data(dax_tickers, period="2y")
    euro_data = download_daily_data(euro_tickers, period="2y")

    reference_sp = build_reference_df(sp_data, sp_tickers)
    reference_nq = build_reference_df(nq_data, nq_tickers)
    reference_dax = build_reference_df(dax_data, dax_tickers)
    reference_euro = build_reference_df(euro_data, euro_tickers)

    df_sp = compute_realtime_evolution(sp_tickers, reference_sp)
    df_nq = compute_realtime_evolution(nq_tickers, reference_nq)
    df_dax = compute_realtime_evolution(dax_tickers, reference_dax)
    df_euro = compute_realtime_evolution(euro_tickers, reference_euro)

    top_sp, worst_sp = rank_performers(df_sp)
    top_nq, worst_nq = rank_performers(df_nq)
    top_dax, worst_dax = rank_performers(df_dax)
    top_euro, worst_euro = rank_performers(df_euro)

    top_sp["Currency"] = "USD"
    worst_sp["Currency"] = "USD"

    top_nq["Currency"] = "USD"
    worst_nq["Currency"] = "USD"

    top_dax["Currency"] = "EUR"
    worst_dax["Currency"] = "EUR"

    top_euro["Currency"] = "EUR"
    worst_euro["Currency"] = "EUR"

    print("=== S&P 500: Top 10 Performers ===")
    print(top_sp[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

    print("=== S&P 500: Worst 10 Performers ===")
    print(worst_sp[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

    print("=== Nasdaq-100: Top 10 Performers ===")
    print(top_nq[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

    print("=== Nasdaq-100: Worst 10 Performers ===")
    print(worst_nq[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

    print("=== DAX: Top 10 Performers ===")
    print(top_dax[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

    print("=== DAX: Worst 10 Performers ===")
    print(worst_dax[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

    print("=== Euronext 100: Top 10 Performers ===")
    print(top_euro[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

    print("=== Euronext 100: Worst 10 Performers ===")
    print(worst_euro[["Name","Live_Price","Prev_Close","%_vs_Prev_Close","%_vs_1W_Ago","%_vs_1M_Ago","%_vs_1Y_Ago","Industry","Sector"]])

print("NaN count in % column:", df_sp["%_vs_Prev_Close"].isna().sum())
print("Non-NaN count:", df_sp["%_vs_Prev_Close"].notna().sum())





