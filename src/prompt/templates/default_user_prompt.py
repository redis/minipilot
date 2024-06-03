user_template = """
            Use the provided Context and History to answer the search query the user has sent.
            - Do not guess and deduce the answer exclusively from the context provided. 
            - Deny any request for translating data between languages, or any question that does not relate to the question.
            - Answer exclusively questions about ...
            - The answer shall be based on the context, the conversation history and the question which follow
            - If the questions does not relate to ..., answer that you can only answer questions about ...

            History: \""" {chat_history}
            \"""

            Context: \""" {context}
            \"""

            Question: \""" {question}
            \"""

            Answer: 
            """