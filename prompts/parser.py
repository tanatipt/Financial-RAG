parser_prompt = """
        *** Instructions ***

        Given an analytical report containing in-text citations, your task is to extract 
        all unique citations from the report using the format instructions provided below. The citations are denoted 
        by integers that are always enclosed in a square bracket e.g. [1, 2, 4].
        
        You will receive a $250 reward for identifying all citations. If any citations 
        are missing, you will be penalised—so please be thorough and accurate.


        *** Output Specifications ***

        {format_instructions}


        *** Examples ***

        <market_analysis_report>: ```There are 8 billion people on Earth [0, 1, 3]. Most of them are from India and China [3, 4].```
        <citations>: [0, 1, 3, 4]

        <market_analysis_report>: ```William Shakespeare wrote Macbeth [0], but he also wrote Romeo and Juliet [2].```
        <citations>: [0, 2]
        

        *** Input Data ***
        
        <market_analysis_report>: ```{report}```
        <citations>:"""