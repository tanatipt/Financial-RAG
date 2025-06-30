from pydantic import BaseModel , Field
from langchain.prompts import PromptTemplate
from typing_extensions import List, Literal, Set, Dict, Annotated
from prompts.examples import summary_crypto, summary_stock, email_crypto, email_stock
from components.example_selector import CustomExampleSelector
from langchain_core.output_parsers import PydanticOutputParser
from langchain.docstore.document import Document
from datetime import datetime
from prompts.summary import summarise_prompt
from prompts.grading import hallucination_prompt, usefulness_prompt
from prompts.email_formatter import email_format_prompt
from prompts.parser import parser_prompt
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.config import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from components.schema import State, Citations, SupportedOutput, UsefulnessOutput
from components.news_retrievers import retrieve_finviz_news, retrieve_google_news, retrieve_tv_news, retrieve_yfinance_news


def create_pipeline():    

    def choose_sources(state : State):
        if state.trading_info.asset_type == "cryptocurrency":
            return ['retrieve_tv_news', 'retrieve_yfinance_news']
        else:
            return ['retrieve_tv_news', 'retrieve_yfinance_news', 'retrieve_finviz_news']

    def filter_trading_news(state : State) -> State:

        # Can add relevancy grader here
        if state.google_search == "yes":
            daily_docs = state.filtered_docs
        else:
            daily_docs = state.daily_docs

        link_ids = set()
        filtered_docs = []

        for doc in daily_docs:
            link = doc.metadata["link"]

            if link in link_ids: continue
            link_ids.add(link)
            filtered_docs.append(doc)


        return {'filtered_docs' : filtered_docs}

    def analyse_market_sentiment(state : State,  config: RunnableConfig) -> State:
        summary_example = example_selector.select_examples({"asset_type" : state.trading_info.asset_type, "current_node" : config["metadata"]["langgraph_node"]})
        docs = state.filtered_docs
        formatted_docs = "\n\n".join([f"News Source ID: {i}\nNews Article Title: {doc.metadata['title']}\nNews Article Body: {doc.page_content}" for i, doc in enumerate(docs)])
        report_chain = PromptTemplate.from_template(summarise_prompt) | model
        report = report_chain.invoke({"symbol_alias" : state.trading_info.symbol_alias, "articles" : formatted_docs, "asset_type" : state.trading_info.asset_type, "summary_example" : summary_example}).content

        return {"report" : report}

    def extract_citations(state: State) -> State:
        parser = PydanticOutputParser(pydantic_object=Citations)

        parser_chain = PromptTemplate.from_template(parser_prompt, partial_variables={"format_instructions" : parser.get_format_instructions()}) | model | parser
        citations = parser_chain.invoke({"report" : state.report}).citations
        cited_docs = [(i, doc) for i, doc in enumerate(state.filtered_docs) if i in citations]

        return {"cited_docs" : cited_docs}




    def grade_generation(state : State) :
    
        cited_docs = state.cited_docs
        formatted_docs = "\n\n".join([f"News Article Title: {doc.metadata['title']}\nNews Article Body: {doc.page_content}" for _, doc in cited_docs])

        hallucination_chain = PromptTemplate.from_template(hallucination_prompt) | model.with_structured_output(SupportedOutput)
        is_supported = hallucination_chain.invoke({"report" : state.report, "document" : formatted_docs }).is_supported


        usefulness_chain = PromptTemplate.from_template(usefulness_prompt) | model.with_structured_output(UsefulnessOutput)
        is_useful = usefulness_chain.invoke({"report" : state.report, "symbol_alias" : state.trading_info.symbol_alias}).is_useful

        if int(is_supported) >= 4 and is_useful == "yes":
            return {"status" : "success"}
        else:
            return {"status" : "failure"}
        
    def decide_to_format(state : State) -> Literal['email_formatter', 'retrieve_google_news', '__end__']:
        status = state.status
        google_search = state.google_search

        if status == 'success':
            return "email_formatter" 
        else:
            if google_search == "yes":
                return "__end__"
            else:
                return "retrieve_google_news"

    def email_formatter(state : State, config : RunnableConfig) -> State:
        formatting_example = example_selector.select_examples({"asset_type" : state.trading_info.asset_type, "current_node" : config["metadata"]["langgraph_node"]})
        email_format_chain = PromptTemplate.from_template(email_format_prompt) | model
        cited_docs = state.cited_docs
        source_w_link = "\n\n".join([f"News Source ID:{i}\nNews Article Title: {doc.metadata['title']}\nNews Article Link: {doc.metadata['link'] if doc.metadata['link'] != '' else '[Link Unavailable]'}" for i,doc in cited_docs])
        email_content = email_format_chain.invoke({"report" : state.report, "symbol_alias" : state.trading_info.symbol_alias, "citations" : source_w_link, "asset_type" : state.trading_info.asset_type, "formatting_example" : formatting_example}).content


        return {"report" : email_content}

    example_selector = CustomExampleSelector({ "ss" : summary_stock, "sc" : summary_crypto, "ec": email_crypto, "es" : email_stock})
    model = ChatGoogleGenerativeAI(model = "gemini-2.0-flash", temperature = 0.0, top_p = 0.0)
    workflow = StateGraph(State)

    workflow.add_node("retrieve_tv_news", retrieve_tv_news)
    workflow.add_node("retrieve_google_news", retrieve_google_news)
    workflow.add_node("retrieve_finviz_news", retrieve_finviz_news)
    workflow.add_node("retrieve_yfinance_news", retrieve_yfinance_news)    

    workflow.add_node("filter_trading_news", filter_trading_news)
    workflow.add_node("analyse_market_sentiment", analyse_market_sentiment)
    workflow.add_node("extract_citations", extract_citations)
    workflow.add_node('email_formatter', email_formatter)
    workflow.add_node("grade_generation", grade_generation)

    workflow.add_conditional_edges(START, choose_sources)

    workflow.add_edge("retrieve_tv_news", "filter_trading_news")
    workflow.add_edge("retrieve_finviz_news", "filter_trading_news")
    workflow.add_edge("retrieve_yfinance_news", "filter_trading_news")

    workflow.add_edge("filter_trading_news", "analyse_market_sentiment")
    workflow.add_edge("analyse_market_sentiment", "extract_citations")
    workflow.add_edge("extract_citations", "grade_generation")
    workflow.add_conditional_edges("grade_generation", decide_to_format)
    workflow.add_edge("retrieve_google_news", "filter_trading_news")
    workflow.add_edge('email_formatter', END)

    graph = workflow.compile()

    return graph
