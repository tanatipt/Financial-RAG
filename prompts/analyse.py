analyse_prompt = """
You are provided with a list of news articles. Your task is to analyze the current market sentiment for {symbol_alias}, based solely on the information contained in these articles. If any projected or forecasted sentiment is mentioned, please identify and include it in your report.

Your analysis must be logical, accurate, and entirely supported by the content of the provided articles. If your analysis meets these criteria and is deemed accurate, you will be awarded $250.

However, you will be fined up to $2500 and face imprisonment for 10 year if found guilty of any of the following violations:
-Including incorrect or irrelevant citations that do not support the claims made in your analysis.
-Making claims in your analysis that are not explicitly stated or reasonably inferred from the articles.
-Providing a sentiment classification other than one of the following: "Strongly Negative", "Negative", "Neutral", "Positive", or "Strongly Positive".
For forecasted sentiment, the above values apply, but None is also acceptable if no projection is provided in the articles.
"""