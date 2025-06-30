from gnews import GNews
from newspaper import Article
from finvizfinance.quote import finvizfinance
from googlenewsdecoder import gnewsdecoder
import yfinance as yf
from tradingview_scraper.symbols.news import NewsScraper
from datetime import datetime, timedelta
from langchain.docstore.document import Document
from zoneinfo import ZoneInfo
from components.schema import State

def retrieve_google_news(state : State) -> State:
    start_date = state.executed_time - timedelta(days = 7)
    google_news = GNews(start_date=start_date , max_results=50)
    if state.trading_info.trading_exchange == "NASDAQ":
        query = f"{state.trading_info.trading_exchange }:{state.trading_info.trading_symbol}"
    else:
        query = f"{state.trading_info.symbol_alias} {state.trading_info.trading_symbol[:-4]}"
    
    news_result = google_news.get_news(query)
    docs = []

    for news in news_result:
        try :
            url = news["url"]
            title = news['title']
            pub_date = datetime.strptime(news['published date'], "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=ZoneInfo('GMT')).astimezone(ZoneInfo('Asia/Bangkok'))
            decoded_url = gnewsdecoder(url)

            if decoded_url['status'] and pub_date >= start_date:
                article = Article(decoded_url["decoded_url"])
                article.download()
                article.parse()

                
                link = article.url
                source = news['publisher'].get("title", "")
                body = article.text 

                if len(body) == 0 : continue
                doc = Document(page_content = body,  metadata = {"published_date" : pub_date, "link" : link, "source" : source, "title" : title})
                docs.append(doc)
        except : continue

    return {"filtered_docs" : docs, "google_search" : "yes"}

def retrieve_yfinance_news(state: State):
    start_date = state.executed_time - timedelta(days = 7)
    if state.trading_info.asset_type == "cryptocurrency":
        ticker = f"{state.trading_info.trading_symbol[:-4]}-USD"
    else:
        ticker = state.trading_info.trading_symbol

    dat = yf.Ticker(ticker)
    results = dat.get_news(count = 15)
    docs = []


    for news in results:

        try:
            content_type = news['content']['contentType']
            pub_date = news['content']['pubDate']
            pub_date = datetime.strptime(pub_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Bangkok'))
            source = news['content']['provider']['displayName']
            title = news['content']['title']
            link = news['content']['canonicalUrl']['url']

            if content_type == "STORY" and pub_date >= start_date: 
                article = Article(link)
                article.download()
                article.parse()
                
                body = article.text 
                if len(body) == 0 : continue

                doc = Document(page_content = body,  metadata = {"published_date" : pub_date, "link" : link, "source" : source, "title" : title})
                docs.append(doc)
        except: continue

    return {"daily_docs" : docs}

def retrieve_finviz_news(state : State):
    start_date = state.executed_time - timedelta(days = 7)
    stock = finvizfinance(state.trading_info.trading_symbol)
    news = stock.ticker_news()
    news['Date'] = news['Date'].dt.tz_localize('US/Eastern').dt.tz_convert("Asia/Bangkok")
    news = news[news['Date'] >= start_date]
    docs = []

    for row in news.itertuples(index=False):
        try : 
            title = row.Title
            source = row.Source
            link = row.Link
            pub_date = row.Date

            if link.startswith("/news"):
                link = f"https://finviz.com{link}"

            article = Article(link)
            article.download()
            article.parse()

            body = article.text

            if len(body) == 0 : continue

            doc = Document(page_content = body,  metadata = {"published_date" : pub_date, "link" : link, "source" : source, "title" : title})
            docs.append(doc)
        except : continue

    return {"daily_docs" : docs}

def retrieve_tv_news(state : State):
    start_date = state.executed_time - timedelta(days = 7)
    docs = []
    news_scraper = NewsScraper()
    news_headlines = news_scraper.scrape_headlines(
        symbol=state.trading_info.trading_symbol,     
        exchange=state.trading_info.trading_exchange, 
        sort='latest'
    )

    for headline in news_headlines:
        try:
            content =news_scraper.scrape_news_content(headline.get('storyPath', ""))
            pub_date = datetime.strptime(content['published_datetime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Bangkok'))

            if pub_date >= start_date:
                if len(content['body']) == 0: continue
                body = "\n".join([p['content'] for p in content['body'] if p['type'] == "text"])
                doc = Document(page_content=body, metadata = {"published_date" : pub_date, "link" : headline.get('link', ""), "source" : headline.get('source', ""), "title" : headline.get('title', "")})
                docs.append(doc)
            else:
                break
        except: continue

    return {"daily_docs" : docs}