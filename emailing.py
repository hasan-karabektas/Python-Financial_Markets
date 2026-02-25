import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz
import pandas as pd


def dataframe_to_html(df):

    df = df[[
        "Name",
        "Live_Price",
        "Prev_Close",
        "Prev_Close_Date",
        "%_vs_Prev_Close",
        "%_vs_1W_Ago",
        "%_vs_1M_Ago",
        "%_vs_1Y_Ago",
        "Industry",
        "Sector",
        "Currency"
    ]]

    def format_price(row, column_name):
        val = row[column_name]

        if val is None or pd.isna(val):
            return "N/A"

        currency = row.get("Currency", "EUR")

        try:
            if currency == "USD":
                return f"${val:,.2f}"
            elif currency == "EUR":
                return f"€{val:,.2f}"
            else:
                return f"{val:,.2f} {currency}"
        except (TypeError, ValueError):
            return "N/A"

    df["Live_Price"] = df.apply(lambda row: format_price(row, "Live_Price"), axis=1)
    df["Prev_Close"] = df.apply(lambda row: format_price(row, "Prev_Close"), axis=1)

    percent_cols = [
        "%_vs_Prev_Close",
        "%_vs_1W_Ago",
        "%_vs_1M_Ago",
        "%_vs_1Y_Ago"
    ]

    for col in percent_cols:
        df[col] = df[col].map(lambda x: f"{x:.2f}%")

    df["Name"] = df["Name"].apply(lambda x: f"<b>{x}</b>")
    df["%_vs_Prev_Close"] = df["%_vs_Prev_Close"].apply(lambda x: f"<b>{x}</b>")

    df = df.drop(columns=["Currency"])

    return df.to_html(index=False, border=0, classes="data-table", escape=False)


def build_index_section(index_name, top_df, worst_df, currency):

    top_df = top_df.copy()
    worst_df = worst_df.copy()

    top_df["Currency"] = currency
    worst_df["Currency"] = currency

    top_html = dataframe_to_html(top_df)
    worst_html = dataframe_to_html(worst_df)

    section = f"""
    <h2>{index_name}</h2>

    <div class="top-box">
        <h3>Top Performers</h3>
        {top_html}
    </div>

    <br>

    <div class="worst-box">
        <h3>Worst Performers</h3>
        {worst_html}
    </div>

    <hr>
    """

    return section


def send_email(subject, html_content, EMAIL_USER, EMAIL_PASS, EMAIL_TO):

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("Email successfully sent.")

if __name__ == "__main__":

    from realtime_evolution import build_index_evolution
    from sp_list import get_sp500_tickers
    from nasdaq_list import get_nasdaq100_tickers
    from dax_list import get_dax_tickers
    from euronext_list import get_euronext100_tickers

    sp500_df = get_sp500_tickers()
    nasdaq_df = get_nasdaq100_tickers()
    dax_df = get_dax_tickers()
    euro_df = get_euronext100_tickers()

    if "Symbol" in dax_df.columns:
        dax_df = dax_df.rename(columns={"Symbol": "Ticker"})

    sp500_df = sp500_df.rename(columns={"Symbol": "Ticker"})
    nasdaq_df = nasdaq_df.rename(columns={"Ticker": "Ticker"})  # harmless
    
    
    sp_tickers = sp500_df["Ticker"].tolist()
    nq_tickers = nasdaq_df["Ticker"].tolist()
    dax_tickers = dax_df["Ticker"].tolist()
    euro_tickers = euro_df["Ticker"].tolist()

    print("SP500 rows:", len(sp500_df))
    print("NASDAQ rows:", len(nasdaq_df))
    print("DAX rows:", len(dax_df))
    print("EURO rows:", len(euro_df))

    top_sp, worst_sp = build_index_evolution(sp_tickers)
    top_nq, worst_nq = build_index_evolution(nq_tickers)
    top_dax, worst_dax = build_index_evolution(dax_tickers)
    top_euro, worst_euro = build_index_evolution(euro_tickers)

    cet = pytz.timezone("Europe/Paris")
    now = datetime.now(cet).strftime("%Y-%m-%d %H:%M CET")

    html_template = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial;
                background-color: #f4f4f4;
            }}

            .data-table {{
                border-collapse: collapse;
                width: 100%;
                background-color: white;
            }}

            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 6px;
                text-align: center;
            }}

            .data-table th {{
                background-color: #1f2937;
                color: white;
                font-weight: bold;
            }}

            .top-box {{
                border: 3px solid green;
                padding: 10px;
                background-color: #f0fff0;
            }}

            .worst-box {{
                border: 3px solid red;
                padding: 10px;
                background-color: #fff0f0;
            }}

        </style>
    </head>

    <body>

    <h1>Financial Markets Evolution Report</h1>
    <p><strong>Generated:</strong> {now} | Data source: Yahoo Finance</p>

    {build_index_section("S&P 500", top_sp, worst_sp, "USD")}  
    {build_index_section("Nasdaq-100", top_nq, worst_nq, "USD")}
    {build_index_section("DAX", top_dax, worst_dax, "EUR")}
    {build_index_section("Euronext 100", top_euro, worst_euro, "EUR")}

    </body>
    </html>
    """
    import os
    send_email(
        subject="Financial Markets Evolution Report",
        html_content=html_template,
        EMAIL_USER = os.getenv("EMAIL_USER"),
        EMAIL_PASS = os.getenv("EMAIL_PASS"),
        EMAIL_TO   = os.getenv("EMAIL_TO")

    )




