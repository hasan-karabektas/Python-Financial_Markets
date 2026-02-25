import yfinance as yf

def download_daily_data(tickers, period="2y"):
    data = yf.download(
        tickers,
        period=period,
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        threads=True
    )
    return data




