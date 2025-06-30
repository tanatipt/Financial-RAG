from components.summarise_pipeline import create_pipeline
from components.schema import TradingInfo
from config import settings
import os
import logging
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

logging.basicConfig(level = logging.INFO)

load_dotenv()

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())

def format_sections(sections):
    formatted_sections = "\n\n".join(sections)
    return  f"""
        <!DOCTYPE html>
        <html lang="en">
        <body>
            {formatted_sections}
        </body>
        </html>
    """
trading_exchanges = ["NASDAQ", "BINANCE"]

sender = os.getenv("GMAIL_ADDRESS")
recipients = [os.getenv("GMAIL_ADDRESS")]
password = os.getenv("GMAIL_PASSWORD")

current_time = datetime.now(ZoneInfo('Asia/Bangkok'))
current_day = current_time.strftime('%Y-%m-%d')
summarise_pipeline = create_pipeline()

for exchange in trading_exchanges:

    if exchange == "BINANCE":
        subject = f"{current_day} Crypto Sentiment Report"
        asset_type = "cryptocurrency"
    else:
        subject = f"{current_day} Stocks Sentiment Report"
        asset_type = "stocks"

    trading_symbols = settings[exchange]
    sections = []

    for trading_alias, trading_symbol in trading_symbols.items():
        trading_info = TradingInfo(trading_symbol=trading_symbol, trading_exchange=exchange, symbol_alias=trading_alias, asset_type=asset_type)
        response = summarise_pipeline.invoke({"executed_time" : current_time, "trading_info" : trading_info})
        status = response["status"]

        if status == "failure":
            logging.error(f"Analytical Report Generation for {trading_symbol} Failed. Please check Langsmith.")
        else:
            logging.info(f"Analytical Report Generation for {trading_symbol} Succeeded.")
            section = response["report"].strip("`").removeprefix("html\n")
            sections.append(section)

        time.sleep(30)

    if len(sections) > 0:
        formatted_html = format_sections(sections)
        send_email(subject, formatted_html, sender, recipients, password)