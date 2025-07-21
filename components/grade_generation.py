from langchain.prompts import PromptTemplate
from prompts.grading import hallucination_prompt, usefulness_prompt
from components.schemas import State, GroundednessOutput, UsefulnessOutput
from langchain_core.language_models.chat_models import BaseChatModel
from typing_extensions import Literal
from langchain_core.prompts.chat import ChatPromptTemplate

def grade_generation(state: State, model : BaseChatModel, symbol_alias : str) -> Literal['email_formatter', 'analyse_sentiment', '__end__']:
    """
    Evaluates the generated market sentiment report for groundedness and usefulness.
    Args:
        state (State): The current pipeline state containing the sentiment report and news articles.
        model (BaseChatModel): The language model used for grading the report.
        symbol_alias (str): The alias for the trading symbol being analyzed.
    Returns:
        Literal: The next node to transition to based on the grading results.
    """

    report = state.report
    # Prepare the cited news articles for the grading process
    formatted_cited_news = "\n\n".join([
        f"""
        Source ID:{i}
        News Title: {doc.metadata['title']}
        News Link: {doc.metadata['link'] if doc.metadata['link'] != '' else '[Link Unavailable]'}
        News Full Text: {doc.page_content.strip()}""" 
        for i,doc in enumerate(state.retrieved_news) if i in report.e_citations
    ])
    human_msg = """<sentiment_report>:{report}\n<cited_news>:{cited_news}"""
    hallucination_pt = ChatPromptTemplate(
        [
            ('system', hallucination_prompt),
            ('human', human_msg)
        ]
    )
    # Create a prompt template for the groundedness evaluation
    hallucination_chain = hallucination_pt | model.with_structured_output(GroundednessOutput)
    # Invoke the model to evaluate the groundedness of the report
    groundedness_score = hallucination_chain.invoke({"report" : report.b_report, "cited_news" : formatted_cited_news}).b_is_grounded


    human_msg = """<sentiment_report>:{report}"""
    useful_pt = ChatPromptTemplate(
        [
           ('system', usefulness_prompt),
           ('human', human_msg) 
        ]
    )
    # Create a prompt template for the usefulness evaluation
    useful_chain = useful_pt | model.with_structured_output(UsefulnessOutput)
    # Invoke the model to evaluate the usefulness of the report
    usefulness_score = useful_chain.invoke({"report" : report.b_report, 'symbol_alias' : symbol_alias}).b_is_useful

    # Determine the next node based on the evaluation scores
    if usefulness_score== 'yes' and groundedness_score == "yes":
        return 'email_formatter'
    elif usefulness_score == 'yes' and groundedness_score == 'no':
        return 'analyse_sentiment'
    else:
        return '__end__'
    
