from components.graph_constructor import GraphConstructor
from config import settings
import os
import logging
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo
from typing_extensions import List
from dotenv import load_dotenv

logging.basicConfig(level = logging.INFO)

load_dotenv()

def send_email(subject : str, body : str, sender : str, recipients : str, password : str):
    """Send an email with the given subject and body.

    Args:
        subject (str): Email subject
        body (str): Body of the email
        sender (str): Email sender address
        recipients (str): List of recipient email addresses
        password (str): Sender's email password
    """
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())

def format_sections(sections : List):
    """
        Formats a list of section strings into an HTML document.

        Args:
            sections (List): A list of strings, each representing a section to be included in the HTML body.

        Returns:
            str: A string containing the formatted HTML document with the sections joined by double newlines.
    """
    formatted_sections = "\n\n".join(sections)
    return  f"""
        <!DOCTYPE html>
        <html lang="en">
        <body>
            {formatted_sections}
        </body>
        </html>
    """


if __name__ == "__main__":
    # List of exchanges to process
    trading_exchanges = ["BINANCE","NASDAQ"]

    # Email credentials and recipients from environment variables
    sender = os.getenv("GMAIL_ADDRESS")
    recipients = [os.getenv("GMAIL_ADDRESS")]
    password = os.getenv("GMAIL_PASSWORD")

    # Get current time in Asia/Bangkok timezone
    current_time = datetime.now(ZoneInfo('Asia/Bangkok'))
    current_day = current_time.strftime('%Y-%m-%d')

    # Iterate over each exchange
    for exchange in trading_exchanges:

        # Set subject and asset type based on exchange
        if exchange == "BINANCE":
            subject = f"{current_day} Crypto Sentiment Report"
            asset_type = "cryptocurrency"
        else:
            subject = f"{current_day} Stocks Sentiment Report"
            asset_type = "stocks"

        trading_symbols = settings.target_assets[exchange]
        sections = []

        # Iterate over each trading symbol in the exchange
        for i, (trading_alias, trading_symbol) in enumerate(trading_symbols.items()):
            print(trading_symbol)
            try:
                graph = GraphConstructor(asset_type = asset_type, trading_symbol=trading_symbol, trading_exchange=exchange, symbol_alias=trading_alias).compile()
                response = graph.invoke(input = {},config={"recursion_limit": 6})
                # Log and handle report generation status
                if len(response['email']) == 0:
                    logging.error(f"Analytical Report Generation for {trading_symbol} Failed. Please check Langsmith.")
                else:
                    logging.info(f"Analytical Report Generation for {trading_symbol} Succeeded.")
                    section = response["email"].strip("`").removeprefix("html\n")
                    sections.append(section)
            except Exception as e:
                continue
            finally:
                time.sleep(30) # Sleep to avoid rate limits or API throttling


        # If there are sections, format and send the email
        if len(sections) > 0:
            formatted_html = format_sections(sections)
            send_email(subject, formatted_html, sender, recipients, password)