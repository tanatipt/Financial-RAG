from langchain_core.example_selectors.base import BaseExampleSelector

class CustomExampleSelector(BaseExampleSelector):
    def __init__(self, examples):
        self.examples = examples

    def add_example(self, example):
        self.examples.append(example)

    def select_examples(self, input_variables):
        asset_type = input_variables["asset_type"]
        current_node = input_variables['current_node']

        if current_node == "email_formatter" and asset_type == "cryptocurrency":
            return self.examples['ec']
        elif current_node == "email_formatter" and asset_type == "stocks":
            return self.examples['es']
        elif current_node == "analyse_market_sentiment" and asset_type == "cryptocurrency":
            return self.examples['sc']
        else:
            return self.examples['ss']