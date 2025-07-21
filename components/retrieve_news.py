from newspaper import Article
from finvizfinance.quote import finvizfinance
import yfinance as yf
from tradingview_scraper.symbols.news import NewsScraper
from datetime import datetime, timedelta
from langchain.docstore.document import Document
from zoneinfo import ZoneInfo
from components.schemas import State
from typing_extensions import List

def retrieve_news(state : State, trading_symbol: str, asset_type : str, trading_exchange : str) -> State:
    """
    Retrieves and filters news articles relevant to the specified trading symbol and asset type.
    Args:
        state (State): The current pipeline state.
        trading_symbol (str): The trading symbol for which news articles are to be retrieved.
        asset_type (str): The type of asset (e.g., 'stocks', 'cryptocurrency').
        trading_exchange (str): The exchange where the asset is traded (e.g., 'NASDAQ').
    Returns:
        State: A dictionary containing the retrieved and formatted news articles.
    """
    # Get current time in Asia/Bangkok timezone
    current_time = datetime.now(ZoneInfo('Asia/Bangkok'))
    # Retrieve news articles from various sources
    yfinance_news = retrieve_yfinance_news(current_time, trading_symbol, asset_type)
    #tv_news = retrieve_tv_news(executed_time=current_time, trading_symbol=trading_symbol, trading_exchange=trading_exchange)

    news = yfinance_news #+ tv_news

    #if asset_type == "stocks":
    #    finviz_news = retrieve_finviz_news(executed_time=current_time, trading_symbol=trading_symbol)
    #    news += finviz_news

    # Filter out duplicate news articles based on their links
    filtered_news = filter_trading_news(news)
    # Format the filtered news articles for further processing
    formatted_news = "\n\n".join([
        f"""
        Source ID:{i}
        News Title: {doc.metadata['title']}
        News Link: {doc.metadata['link'] if doc.metadata['link'] != '' else '[Link Unavailable]'}
        News Full Text: {doc.page_content.strip()}""" 
        for i,doc in enumerate(filtered_news)
    ])

    return {'retrieved_news' : filtered_news, "formatted_news" : formatted_news}

    

def filter_trading_news(docs : List) -> List:
    """
    Filters out duplicate news articles based on their links.

    Args:
        docs (List): A list of Document objects containing news articles.

    Returns:
        List: A list of Document objects with duplicate articles removed based on their links.
    """

    link_ids = set()
    filtered_docs = []

    for doc in docs:
        link = doc.metadata["link"]

        if link in link_ids: continue
        link_ids.add(link)
        filtered_docs.append(doc)


    return filtered_docs


def retrieve_yfinance_news(executed_time : datetime, trading_symbol : str, asset_type : str) -> List:
    """
    Retrieves news articles for the specified trading symbol using yfinance.

    Args:
        executed_time (datetime): The time when the news retrieval is executed.
        trading_symbol (str): The trading symbol for which news articles are to be retrieved.
        asset_type (str): The type of asset (e.g., 'stocks', 'cryptocurrency').

    Returns:
        List: A list of Document objects containing the retrieved news articles.
    """
    # Calculate the start date (7 days ago from execution time)
    start_date = executed_time - timedelta(days = 7)
    # Format ticker for cryptocurrencies, otherwise use trading symbol
    if asset_type == "cryptocurrency":
        ticker = f"{trading_symbol[:-4]}-USD"
    else:
        ticker = trading_symbol

    # Retrieve news articles using yfinance
    data = yf.Ticker(ticker)
    results = data.get_news(count = 30)
    docs = []

    # Iterate over each news result
    for news in results:
        try:
            content_type = news['content']['contentType']
            pub_date = news['content']['pubDate']
            # Parse and convert publication date to Asia/Bangkok timezone
            pub_date = datetime.strptime(pub_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Bangkok'))
            source = news['content']['provider']['displayName']
            title = news['content']['title']
            link = news['content']['canonicalUrl']['url']

            # Only include news of type STORY and published within last 7 days
            if content_type == "STORY" and pub_date >= start_date: 
                # Download and parse article content
                article = Article(link)
                article.download()
                article.parse()
                
                body = article.text 
                # Skip articles with empty body
                if len(body) == 0 : continue

                # Create Document object with article content and metadata
                doc = Document(page_content = body,  metadata = {"published_date" : pub_date, "link" : link, "source" : source, "title" : title})
                docs.append(doc)
        except: 
            # Ignore errors and continue with next news result
            continue

    # Return list of Document objects
    return docs

def retrieve_finviz_news(executed_time : datetime, trading_symbol : str) -> List:
    """
    Retrieves news articles for the specified trading symbol using Finviz.

    Args:
        executed_time (datetime): The time when the news retrieval is executed.
        trading_symbol (str): The trading symbol for which news articles are to be retrieved.

    Returns:
        List: A list of Document objects containing the retrieved news articles.
    """
    # Calculate the start date (7 days ago from execution time)
    start_date =  executed_time - timedelta(days = 7)
    # Retrieve news for the given trading symbol using Finviz
    stock = finvizfinance(trading_symbol)
    news = stock.ticker_news()
    # Localize news dates to US/Eastern and convert to Asia/Bangkok timezone
    news['Date'] = news['Date'].dt.tz_localize('US/Eastern').dt.tz_convert("Asia/Bangkok")
    # Filter news published within the last 7 days
    news = news[news['Date'] >= start_date]
    docs = []

    # Iterate over each news row
    for row in news.itertuples(index=False):
        try : 
            title = row.Title
            source = row.Source
            link = row.Link
            pub_date = row.Date

            # Fix relative Finviz news links
            if link.startswith("/news"):
                link = f"https://finviz.com{link}"

            # Download and parse article content
            article = Article(link)
            article.download()
            article.parse()

            body = article.text

            # Skip articles with empty body
            if len(body) == 0 : continue

            # Create Document object with article content and metadata
            doc = Document(page_content = body,  metadata = {"published_date" : pub_date, "link" : link, "source" : source, "title" : title})
            docs.append(doc)
        except : 
            # Ignore errors and continue with next news row
            continue

    # Return list of Document objects
    return docs

def retrieve_tv_news(executed_time : datetime,trading_symbol : str, trading_exchange : str) -> List:
    """
    Retrieves news articles for the specified trading symbol from TradingView.

    Args:
        executed_time (datetime): The time when the news retrieval is executed.
        trading_symbol (str): The trading symbol for which news articles are to be retrieved.
        trading_exchange (str): The exchange where the asset is traded (e.g., 'NASDAQ').

    Returns:
        List: A list of Document objects containing the retrieved news articles.
    """
    start_date = executed_time - timedelta(days = 7)
    docs = []
    news_scraper = NewsScraper()
    # Scrape latest news headlines for the given symbol and exchange
    news_headlines = news_scraper.scrape_headlines(
        symbol=trading_symbol,     
        exchange=trading_exchange, 
        sort='latest'
    )

    for headline in news_headlines:
        try:
            # Get full news content for each headline
            content = news_scraper.scrape_news_content(headline.get('storyPath', ""))
            # Parse and convert publication date to Asia/Bangkok timezone
            pub_date = datetime.strptime(content['published_datetime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Bangkok'))

            if pub_date >= start_date:
                # Skip articles with empty body
                if len(content['body']) == 0: continue
                # Concatenate all text paragraphs in the body
                body = "\n".join([p['content'] for p in content['body'] if p['type'] == "text"])
                # Create Document object with article content and metadata
                doc = Document(
                    page_content=body,
                    metadata={
                        "published_date": pub_date,
                        "link": headline.get('link', ""),
                        "source": headline.get('source', ""),
                        "title": headline.get('title', "")
                    }
                )
                docs.append(doc)
            else:
                # Stop processing if article is older than start_date
                break
        except:
            # Ignore errors and continue with next headline
            continue

    return docs
