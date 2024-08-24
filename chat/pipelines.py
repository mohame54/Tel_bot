import abc
from typing import Optional
from .llm import chat_from_key
import re


class BasePipeLine(abc.ABC):
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

    def setup(self):
        self.llm.setup()    
    

class ReactPipeline(BasePipeLine):
    def __init__(
        self,
        api_key: str,
        num_top_results: Optional[int] = 2,
        max_num_chars: Optional[int] = None,
        description: Optional[str]="React Agent with tools",
    ):    
        super(ReactPipeline, self).__init__(description)
        self.llm = chat_from_key(
            api_key,
            sys_prompt=SEARCH_SYS_P,
        )
    

    def _check_answer(self, ai_mssg:str) -> str:
        ai_mssg = re.sub(r'</?rules>', '', ai_mssg)
        if "SEARCH_ARTICLE" in ai_mssg:
           match = re.search(r'<([^<>]*)>', ai_mssg)
           if match:
              return match.group(1)
        return ""
    
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
               REMEMBER not to mention the article in your answer and treats it as knowledge you searched on the internet yourself.
            """    
            ai_mssg = self.llm(new_query)
        else:
            ai_mssg = self.llm(user_query)    
        return ai_mssg    
