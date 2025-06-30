from pydantic import BaseModel , Field
from typing_extensions import List, Literal, Set, Dict, Annotated
from langchain.docstore.document import Document
from datetime import datetime

def add_daily_docs(left : list | None, right : list | None):
    if not left:
        left = []

    if not right:
        right = []

    return left + right

class TradingInfo(BaseModel):
    trading_symbol : str = Field("", description = "The trading symbol")
    trading_exchange : Literal['NASDAQ', 'BINANCE'] = Field("", description = "The trading exchange")
    symbol_alias : str = Field("", description = "The symbol alias")
    asset_type: Literal['cryptocurrency', 'stocks'] = Field("", description="The underlying type of asset")

class Citations(BaseModel):
    citations : Set[int] = Field(..., description = "A unique list of integer source IDs for all the news articles that have been cited in the generated market sentiment analytical report.")

class State(BaseModel):
    executed_time : datetime = Field(..., description = "The datetime at which the news analyser is executed.")
    status : Literal["success", "failure"] = Field("success", description = "A flag to indicate whether the analytical report has been succesfully generated")
    daily_docs : Annotated[List[Document], add_daily_docs] = Field([], description = "A list of news articles published today, used as the primary source for sentiment analysis.")
    filtered_docs : List[Document]= Field([], description = "A list of news articles that have been filtered to remove duplicates and content irrelevancy")
    cited_docs : List[tuple]= Field([], description = "A list of news articles that have been used to justify the generated response.")
    report : str = Field("", description= "The analytical report of the current market sentiment, derived from today’s news articles.")
    google_search : Literal["yes", "no"] = Field("no", description="A flag to indicate whether a google news search was performed")
    trading_info : TradingInfo = Field(TradingInfo(), description = "The trading information")

class SupportedOutput(BaseModel):
    is_supported : Literal["1", "2", "3", "4", "5"]= Field(...,description = "A graded response indicating how well the key facts in the generated market sentiment analytical report are explictly or implictly supported by the news articles")

class UsefulnessOutput(BaseModel):
    is_useful : Literal["yes", "no"] = Field(..., description="A flag to indicate whether the generated market sentiment analytical report is useful or not")

