from functools import wraps
import inspect

REACT_SYS_P = """
You are an AI agent designed to answer questions through an iterative process. You have access to the following tools:
{tools_and_role}

IMPORTANT: This is an ITERATIVE PROCESS. You will go through multiple steps before reaching a final answer. Do not try to answer the question immediately.

Follow this format EXACTLY for each iteration:
Thought: [Your reasoning about the current state and what to do next]
Action: [One of: {tool_names}]
Action Input: [Parameters for the action they must be key_word_args seperated in a dict format like a function call (you make one action Input each iteration)]

CRITICAL RULES:
1. You operate in a loop. Each iteration, you provide ONLY Thought, Action, and Action Input.
2. DO NOT generate "Observation" text. Observations will be provided to you after each action.
3. After each observation, start a new iteration with a new Thought.
4. Use ONLY information from observations. Do not use external knowledge or assumptions.
5. You may need multiple iterations to gather enough information. Be patient and thorough.
6. Do NOT try to provide a final answer until you are absolutely certain you have all necessary information.
7. You Should Have good reasoning ability while thought so if there is inderect question you can use math to solve for it.

When you are CERTAIN you have ALL information needed to answer the original question:
Thought: I now have all the information to answer the question
Action: finish
Final Answer: [Your detailed answer, referencing specific observations]

Remember:
- You CANNOT provide a final answer without using the "finish" action.
- Always wait for an observation after each action before starting a new iteration.
- If an observation is unclear or insufficient, use your next action to clarify or gather more information.
- Your goal is to be thorough and accurate, not quick. Take as many iterations as needed use tools as much time as you need to get the best result.

Example workflow:
{example_workflow}

Let's begin!
"""

SEARCH_DOC = """
    Executes a search query and retrieves content from the top search results.
    sometimes returns empty research content so you could increase the num of top results
    and adjust the content length as wanted.


    Args:
        query (str): The search query to be executed.
        text_only (Optional[bool]): If True, returns only the text content from the search results.
                                    If False, returns a list of dictionaries with titles, links, and content.
                                    Defaults to True.
        num_top_results (Optional[int]): The number of top search results to retrieve. Defaults to 2.
        content_length (Optional[int]): The minimum content length required for a result to be included.
                                        Defaults to 400 characters.

    Returns:
        Union[List[Dict[str, str]], str]: 
            - If `text_only` is True, returns a single string containing the concatenated text content from the 
              top search results.
            - If `text_only` is False, returns a list of dictionaries where each dictionary contains:
                - "title": The title of the search result.
                - "link": The URL of the search result.
                - "content": The scraped content of the search result.

    Examples:
        Basic usage with the default number of top results:
        
        >>> search_tool = SearchTool()
        >>> results = search_tool(query="Python programming")
        
        Specifying a custom number of top results:
        
        >>> search_tool = SearchTool()
        >>> results = search_tool(query="Machine learning", num_top_results=3)            
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


def has_multiple_arguments(func):
    sig = inspect.signature(func)
    parameters = sig.parameters
    return len(parameters) > 1
