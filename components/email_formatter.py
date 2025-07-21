from prompts.email_formatter import email_format_prompt
from components.schemas import State
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts.chat import ChatPromptTemplate


def email_formatter(state : State, model:  BaseChatModel, symbol_alias : str) -> State:
    """
    Formats the sentiment report into a structured HTML email newsletter.
    Args:
        state (State): The current pipeline state.
        model (BaseChatModel): The language model used for formatting the content of the email.
        symbol_alias (str): The alias for the trading symbol being analyzed.
    Returns:
        State: The formatted email content based on the sentiment report."""

    report = state.report
    # Prepare the cited links for the email content
    cited_links = [
        f"""
        Source ID:{i}
        News Title: {doc.metadata['title']}
        News Link: {doc.metadata['link'] if doc.metadata['link'] != '' else '[Link Unavailable]'}""" 
        for i,doc in enumerate(state.retrieved_news) if i in report.e_citations
    ]

    human_msg = """<sentiment_report>:{report}\n<current_sentiment>:{current_sentiment}\n<projected_sentiment>:{projected_sentiment}\n<cited_links>:{cited_links}"""
    format_pt = ChatPromptTemplate(
        [
            ('system', email_format_prompt),
            ('human', human_msg )
        ]
    )

    format_chain = format_pt | model
    # Invoke the model to format the sentiment report to a HTML newsletter
    email_content = format_chain.invoke(
        {
            "report" : report.b_report,
            "cited_links" : cited_links,
            "symbol_alias" : symbol_alias,
            "current_sentiment" : report.c_current_sentiment_classification,
            "projected_sentiment": report.d_future_sentiment_classification
        }
    ).content

    return {"email" : email_content}