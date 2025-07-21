from prompts.analyse import analyse_prompt
from components.schemas import State, Report
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts.chat import ChatPromptTemplate


def analyse_market_sentiment(state : State, model : BaseChatModel , symbol_alias : str) -> State:
    """
    Analyzes market sentiment based on provided news articles and generates a structured report.

    Args:
        state (State): The current pipeline state.
        model (BaseChatModel): The language model used for generating the sentiment analysis report.
        symbol_alias (str): The alias for the trading symbol being analyzed.
    Returns:
        State: A dictionary containing the generated sentiment report."""
    
    # Retrieve the formatted news articles from the state
    formatted_news = state.formatted_news
    human_msg = """<news_articles>: {formatted_news}"""
    analyse_pt = ChatPromptTemplate(
        [
            ('system', analyse_prompt),
            ('human', human_msg)
        ]
    )

    # Create a prompt template for the sentiment analysis
    report_chain = analyse_pt | model.with_structured_output(Report)
    # Invoke the model to generate the sentiment report
    report = report_chain.invoke(
        {
            "symbol_alias" : symbol_alias, 
            "formatted_news" : formatted_news
        }
    )

    return {"report" : report}