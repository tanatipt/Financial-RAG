from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from components.schemas import State
from components.retrieve_news import retrieve_news
from components.analyse_market_sentiment import analyse_market_sentiment
from components.grade_generation import grade_generation
from components.email_formatter import email_formatter
from config import settings


class GraphConstructor:
    def __init__(
        self, 
        asset_type : str,
        trading_symbol : str, 
        trading_exchange : str,
        symbol_alias : str
        
    ):
        """
        Initializes the graph constructor with the necessary parameters for constructing the workflow graph.

        Args:
            asset_type (str): The type of asset being analyzed (e.g., 'stocks', 'cryptocurrency').
            trading_symbol (str): The trading symbol of the asset being analyzed (e.g., 'NVDA' for Nvidia).
            trading_exchange (str): The exchange where the asset is traded (e.g., 'NASDAQ').
            symbol_alias (str): An alias for the trading symbol, used for formatting and reporting purposes.
        """

        # Initialize the language models for the workflow
        generator_model = ChatGoogleGenerativeAI(model = settings.generator_model.model_name, **settings.generator_model.model_params)
        critic_model = ChatGoogleGenerativeAI(model = settings.critic_model.model_name, **settings.generator_model.model_params)
        # Initialize the nodes of the workflow with the provided parameters
        self.retrieve_news = self.init_node(retrieve_news, trading_symbol=trading_symbol, trading_exchange=trading_exchange, asset_type=asset_type)
        self.analyse_sentiment = self.init_node(analyse_market_sentiment, model = generator_model, symbol_alias = symbol_alias)
        self.grade_generation = self.init_node(grade_generation, model = critic_model, symbol_alias = symbol_alias)
        self.email_formatter = self.init_node(email_formatter, model = generator_model,  symbol_alias = symbol_alias)


        
    def connect_nodes(self) -> StateGraph:
        """
        Connects the nodes of the workflow graph to define the flow of data and control between them.

        Returns:
            StateGraph: A StateGraph object representing the workflow, with nodes connected in a specific order.
        """
        workflow = StateGraph(State)

        workflow.add_node("retrieve_news", self.retrieve_news)
        workflow.add_node("analyse_sentiment", self.analyse_sentiment)
        workflow.add_node('email_formatter', self.email_formatter)

        workflow.add_edge(START, "retrieve_news")
        workflow.add_edge("retrieve_news", "analyse_sentiment")
        workflow.add_conditional_edges("analyse_sentiment", self.grade_generation)
        workflow.add_edge('email_formatter', END)

        return workflow

    def init_node(self, node_function : callable, **kwargs : dict) -> callable:
        """
        Initializes a node function with the provided parameters.

        Args:
            node_function (callable): The function to be wrapped as a node in the workflow.
            **kwargs (dict): Additional keyword arguments to be passed to the node function.

        Returns:
            callable: A wrapped function that takes a State object as input and invokes the original node function with the provided parameters.
        """

        def wrapped_node_function(state : State):
            return node_function(state, **kwargs)
        
        return wrapped_node_function
    
    def compile(self) -> StateGraph:
        """
        Compiles the workflow graph by connecting the nodes and returning the final StateGraph object.

        Returns:
            StateGraph: A StateGraph object representing the complete workflow, ready for execution.
        """
        workflow = self.connect_nodes()
        graph = workflow.compile()

        return graph
    

#graph = GraphConstructor(asset_type = 'stocks', trading_symbol='NVDA', trading_exchange='NASDAQ', symbol_alias='Nvidia').compile()
#results = graph.invoke(input = {})
#print(graph.retrieve_news(state=obj))