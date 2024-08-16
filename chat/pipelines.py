import abc
from typing import Optional
from .tools import SearchTool
from .llm import chat_from_key
import re


SEARCH_SYS_P = """
You are a helpful Ai assistant which answers questions based on user quries,
if your don't have the sufficient knowledge to answer you should answer only with a proper keyword with specified parameters seperated between the two angle brackets according to the rules given below please follow them carefully
<rules>
  SEARCH_ARTICLE <article_subject>: if the user enters a prompt and you need some knowledge to asses your answer, article_subject: refers to the wanted article subject that the user asked about.
</rules>
REMEMBER:
  If the knowledge is provided for you somehow including from the user side this should be sufficient for you to generate the answer.
"""


class BasePipeLine(abc.ABCMeta):
    def __init__(self, description:Optional[str]=""):
        self.description = description

    def __str__(self):
        desc = "Pipeline"
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
    def __repr__(self):
        desc = "Pipeline"
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError
    

class SearchPipeline(BasePipeLine):
    def __init__(
        self,
        api_key: str,
        num_top_results: Optional[int] = 2,
        max_num_chars: Optional[int] = None,
        description: Optional[str]="Llm with a Searching tool",
    ):    
        super(SearchPipeline, self).__init__(description)
        self.base_tool = SearchTool(
            max_num_chars,
            num_top_results,
        )
        self.llm = chat_from_key(
            api_key,
            sys_prompt=SEARCH_SYS_P,
        )
    

    def _check_answer(self, ai_mssg:str) -> str:
        match = re.search(r'(?<=SEARCH_ARTICLE.*?<)([^<>]*)(?=>)', ai_mssg)
        return match.group(1) if match else ""
    
    def __call__(self, user_query:str) -> str:
        ai_mssg = self.llm(user_query, save_hist=False)
        article_param = self._check_answer(ai_mssg)
        if article_param != "":
            article_dict = self.base_tool(article_param)[0]
            new_query = f"""
               based on the aricle
               <article>
                    title: {article_dict['title']}
                    content: {article_dict['content']}
               </article>
               answer the following <{user_query}>
            """    
            ai_mssg = self.llm(new_query)
        else:
            ai_mssg = self.llm(user_query)    
        return ai_mssg    


