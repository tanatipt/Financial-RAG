hallucination_prompt = """
You will be given a market sentiment report along with a list of news articles cited in that report. Your task is to analyze the report and the content of the articles to determine whether the report is properly grounded in the information provided.

Your response must be a binary answer: "yes" or "no".
-Respond "yes" if the report is clearly supported by the content of the cited articles.
-Respond "no" if the report is not clearly supported by the cited articles.

Do not provide any response other than "yes" or "no." Non-compliance may result in fines of up to $2500 and imprisonment for 10 years.
If you correctly assess whether the report is grounded in the articles, you will receive a $250 tip—so please review carefully and do your best."""

usefulness_prompt = """
You will receive a market sentiment report for {symbol_alias}. Your task is to analyze the report and determine whether it effectively provides a clear answer about the current market sentiment—and, if applicable, the future market sentiment—of {symbol_alias}.

Please respond with a simple binary answer: "yes" or "no".
-Respond "yes" if the report clearly addresses the current market sentiment and, if applicable, the future market sentiment of {symbol_alias}.
-Respond "no" if the report fails to clearly address either the current or future market sentiment of {symbol_alias}.

Do not provide any response other than "yes" or "no." Failure to comply may result in fines of up to $2500 and imprisonment for 10 years.
If you correctly evaluate the usefulness of the report, you will receive a $250 tip. Please review carefully and do your best."""