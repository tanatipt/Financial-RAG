# Financial RAG

In this project, we developed a self-reflective RAG with chain-of-thought to analyze a large volume of news articles from the internet and summarize the overall market sentiment for a given asset. As an investor, I’ve always relied on news to build a solid fundamental understanding of the assets I am interested in. However, due to increasing work commitments, I’ve had less time to keep up. To address this, I decided to develop a RAG system that can condense sentiment from multiple news sources into a few concise paragraphs—making it much quicker and easier for me to stay informed. These are the assets I am mainly focused on in this project:

- Cryptocurrency: Bitcoin, Ethereum, Ripple, Binance Coin, Solana and Chainlink
- Stocks: Nvidia, Meta, Tesla, Palantir, Microsoft, Google

## Project Structure

Below is an overview of the project's structure, highlighting the most important files and their roles:
```bash
/components/
├── analyse_market_sentiment.py     # Node for analyzing market sentiment
├── email_formatter.py              # Node for formatting the sentiment report into a weekly HTML newsletter
├── grade_generation.py             # Router for assessing groundedness and usefulness, and directing flow accordingly
├── graph_constructor.py            # Contains the class that connects all nodes to form the final processing graph
├── retrieve_news.py                # Node for retrieving news articles relevant to the given asset
└── schemas.py                      # Defines Pydantic models for graph state and structured generation

/config/
└── settings.yaml                   # Configuration file specifying the LLM model and targeted assets

/prompts/
├── analyse.py                      # System prompt for analyzing market sentiment from news articles
├── email_formatter.py             # System prompt for formatting the report into an HTML newsletter
└── grading.py                      # System prompt for evaluating the groundedness and usefulness of the report

main.py                             # Entry point for running the self-reflective RAG system with chain-of-thought reasoning
```

## Methodology

This section provides a technical overview of the architecture behind our RAG system. The diagram below illustrates the overall architecture of the system. In brief, given a specific asset, the system uses API calls to fetch relevant news articles from the internet. It then analyzes the content to generate a market sentiment report for that asset. Finally, the report is formatted into an HTML-based weekly newsletter and sent via email to the intended recipients. The LLM we used for the RAG is  `gemini-2.5-flash`.

<p align="center">
    <img src='rag_diagram.png' width=400px>
</p>

### Retrieve News Articles

In this node, we retrieve relevant news articles related to a given asset from the internet, using sources that are specific to finance. Specifically, news is fetched via API calls from three platforms: Yahoo Finance (yfinance), TradingView, and Finviz. For cryptocurrencies, only yfinance and TradingView are used, as Finviz does not provide news coverage for these asset types. In contrast, for stocks, all three sources are utilized.

For each source, the retrieved articles are sorted by their publication date and filtered to include only those published within the past week. After collecting the articles, we merge the results from all sources and remove duplicates. To identify duplicates, we assume each article is uniquely defined by its URL and filter out any articles with duplicate links.

Chunking was not necessary during the retrieval process, as the number of articles was relatively small due to the time-based filtering. Moreover, given the approximately 1,000,000-token context window of the `gemini-2.5-flash` model, incorporating all retrieved articles into a single context window poses no issue.

### Analyse Market Sentiment

After retrieving the relevant news articles, we analyzed them to assess the market sentiment for the given asset and generate a comprehensive report detailing both the current sentiment and any projected future trends (if applicable). The report includes citations referencing the specific news articles used in the analysis, ensuring that the information is traceable and verifiable.

To perform the sentiment analysis, we employed a chain-of-thought reasoning approach with structured output. In this method, the model is prompted to first reason through the task, outlining a series of logical steps used to analyse sentiment based on the content of the provided news articles. Each step in the chain represents a discrete reasoning task and the result derived from applying that task to the input data.

The structure of this process is captured using the following Pydantic models:

```python 
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
```

By default, `gemini-2.5-flash` sorts the fields in structured generation alphabetically. This behavior can interfere with the intended reasoning flow if the fields are not named carefully. For instance, if the chain-of-thought is generated after the report, the reasoning becomes ineffective, as we rely on the chain-of-thought to guide the generation of the report itself.

To address this, we prepend alphabetical flags (`a_`, `b_`, `c_`, etc.) to the field names. This ensures that the model generates the output in the desired sequence: first the chain-of-thought, followed by the analytical report. Once the report is generated, the model then concludes the current and projected (if applicable) market sentiment. Finally, it produces the list of citations that support the report.

This naming convention is essential for preserving the logical progression of reasoning, analysis, and conclusion within the model's structured output.


### Self-Reflection

After generating the sentiment report, we perform a self-reflection step that evaluates two key dimensions: groundedness and usefulness. Groundedness assesses whether the content of the report is actually supported by the news articles it cites, while usefulness evaluates whether the report provides a meaningful analysis of the current and projected (if applicable) market sentiment for the asset.

Each assessment yields a binary outcome: `yes` or `no`. A `yes` indicates that the report is grounded and/or useful, while a `no` suggests that the report either contains hallucinated information or fails to provide valuable insight. If the report is found to be hallucinated (i.e., not grounded), we re-generate the report. However, if the report is found to be not useful, we terminate the generation process, as this likely indicates that the retrieved news articles lack sufficient information on market sentiment.

Both evaluations use a chain-of-thought reasoning approach with structured output to analyze the report in the context of the cited news articles. For groundedness, the expected behavior is for the model to examine each claim in the report and assess whether it is supported by evidence from the cited sources. For usefulness, the model is expected to determine whether the report meaningfully discusses both current and projected market sentiment. Once again, we modified the naming conventions of the fields to enforce the correct generation order, due to the gemini-2.5-flash model's behavior of sorting fields alphabetically during structured generation.

```python
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
```

### Email Formatting

We proceed to the email formatting node only if the report has been assessed as both useful and grounded. In this node, the report is formatted into an HTML-based weekly newsletter that will be sent to the recipients. The newsletter includes clearly defined sections such as an introduction, conclusion, and references. To guide the model in producing the desired format, we provide few-shot examples of the expected HTML newsletter structure, encouraging it to generate content that closely follows the provided templates.


## Installation & Project Setup

This section provides instructions on how to install and set up the project locally. Before you begin, please ensure you have the following prerequisites:

1. `Poetry` installed on your system.
2. A valid `GOOGLE_API_KEY` for accessing `gemini-2.5-flash`.
3. A Gmail account for sending emails.
4. `pyenv` installed, along with Python version 3.10.12 managed through `pyenv`.

Steps to Run the RAG System:

1. Create a `pyenv` virtual environment named `financial-rag` using the following command: `pyenv virtualenv 3.10.12 financial-rag`
2. Activate the virtual environment you just created: `pyenv activate financial-rag`
3. Install project dependencies via `Poetry`:  `poetry install`
4. Create a `.env` file in the root directory of the project.
5. Add your credentials to the `.env` file in the following format:
```
GOOGLE_API_KEY=<google_api_key>
GMAIL_PASSWORD=<gmail_password>
GMAIL_ADDRESS=<gmail_address>
```
6. Run the main script to start the RAG system: `python main.py`

