from functools import wraps


REACT_SYS_P = """
You are a helpful Ai assistant which answers questions based on user quries,
if your don't have the sufficient knowledge to answer you should answer only with a proper keyword with specified parameters seperated between the two angle brackets according to the rules given below please follow them carefully
<rules>
  SEARCH_ARTICLE <article_subject>: if the user enters a prompt and you need some knowledge to asses your answer, article_subject: refers to the wanted article subject that the user asked about.
</rules>
REMEMBER:
  If the knowledge is provided for you somehow including from the user side this should be sufficient for you to generate the answer.
"""


SEARCH_DOC =  """
    Executes a web search for the given query and returns summarized content 
    from the top search results.

    Args:
        query (str): The search query to be used for the web search.
        num_top_results (Optional[int]): The number of top search results 
            to retrieve and summarize. Defaults to 2.
        content_length (Optional[int]): the content length limitation because sometimes
            the tool returns empty search content
    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing:
            - "title" (str): The title of the search result.
            - "link" (str): The URL of the search result.
            - "content" (str): The summarized content of the linked web page.

      Examples:
        Basic usage with the default number of top results:
        
        >>> search_tool = SearchTool()
        >>> results = search_tool(query="Python programming")
        >>> for result in results:
        >>>     print(result["title"])
        >>>     print(result["link"])
        >>>     print(result["content"])
        
        Specifying a custom number of top results:
        
        >>> search_tool = SearchTool()
        >>> results = search_tool(query="Machine learning", num_top_results=3)
        >>> for result in results:
        >>>     print(result["title"])
        >>>     print(result["link"])
        >>>     print(result["content"])
"""


PYTHON_EX_DOC =  """
    Executes the provided Python code string and returns the output or error.

    Args:
        code_str (str): The Python code to execute. The code can be in raw 
                        string format or formatted with triple backticks.

    Returns:
        str: The output of the executed code if successful, or the error 
                message if an exception occurred during execution.

    Examples:
        >>> tool = PythonEx()
        >>> output = tool('print("Hello, World!")')
        >>> print(output)
        Output: 
        Hello, World!

        >>> error = tool('raise ValueError("An error occurred!")')
        >>> print(error)
        Error: 
        An error occurred!
"""


def add_docstring(doc):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__doc__ = doc
        return wrapper
    decorator.__doc__ = doc
    return decorator
