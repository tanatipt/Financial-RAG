from pydantic import BaseModel , Field
from typing_extensions import List, Literal
from langchain.docstore.document import Document
from typing_extensions import Optional

class Step(BaseModel):
    """
    A Pydantic model representing a single step in a chain of thought.
    Each step includes a description of the reasoning step and its corresponding output.
    """
    description: str = Field(..., title='Step Description', description="A brief explanation of the reasoning step taken.")
    output: str = Field(..., title='Step Output', description="The result or conclusion derived from this reasoning step.")

class Report(BaseModel):
    """
    A Pydantic model for generating a structured market sentiment analysis report from a list of provided news articles.
    """

    a_chain_of_thought : List[Step] = Field([], title='Chain-of-Thought', description ="A sequence of steps representing a structured approach to solving the task using the content of the provided news articles.", min_length = 1)
    b_report : str = Field('', title='Market Sentiment Report', description ="A detailed analytical report of the current and future (if applicable) market sentiment of the asset, strictly based on the chain-of-thought reasoning.")
    c_current_sentiment_classification : Literal['Strongly Negative', 'Negative', 'Neutral', 'Positive', 'Strongly Positive'] = Field('', title = 'Current Market Sentiment', description ="The concluded current market sentiment based on the analysis presented in the report.")
    d_future_sentiment_classification: Optional[Literal['Strongly Negative', 'Negative', 'Neutral', 'Positive', 'Strongly Positive']] = Field('', title = 'Projected Market Sentiment', description ="The projected future market sentiment (if applicable) based on the report.")
    e_citations : List[int] = Field([], title='Report Citations', description="A list of integer IDs referencing the news articles that support the report.")

class State(BaseModel):
    """
    A Pydantic model representing the state of the workflow, containing retrieved news articles, formatted news, and the sentiment report.
    """
    retrieved_news : List[Document]= Field([], description = "A list of filtered news articles relevant to the current trading symbol.")
    formatted_news : str = Field('', description = "The filtered news articles formatted into a string.")
    report : Report = Field(Report(), description= "The sentiment report of the current and projected (if any) market sentiment and it's citations.")
    email : str = Field('', description = 'The sentiment report that has been formatted into a HTML weekly newsletter.')


class GroundednessOutput(BaseModel):
    """
    A Pydantic model for evaluating whether a market sentiment report is factually grounded in the news articles it references.
    """
    a_chain_of_thought: List[Step] = Field(..., title='Chain-of-Thought', description = "A sequence of steps representing a structured approach to solving the task using the content of the report and cited news articles." , min_length = 1)
    b_is_grounded : Literal["yes", "no"] = Field(..., title = 'Groundedness Score', description ="A binary assessment indicating whether the report is factually grounded in the cited articles, as determined by the chain-of-thought reasoning. ")

class UsefulnessOutput(BaseModel):
    """
    A Pydantic model for evaluating whether a market sentiment report effectively addresses the current and, if applicable, future market sentiment.
    """
    a_chain_of_thought: List[Step] = Field([], title='Chain-of-Thought', description = "A sequence of steps representing a structured approach to solving the task using the content of the report.", min_length = 1)
    b_is_useful : Literal["yes", "no"] = Field(..., title = 'Usefulness Score' , description="A binary assessment indicating whether the report addresses the current and, if applicable, future market sentiment, as determined by the chain-of-thought reasoning.")

