import abc
from typing import Optional, Dict
from .llm import chat_from_key
import re
from tools import ToolKit, REACT_SYS_P, has_multiple_arguments
import warnings



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
        toolkit: ToolKit,
        example_workflow: Optional[str] = "",
        description: Optional[str]="React Agent with tools",
    ):    
        super(ReactPipeline, self).__init__(description)
        self.toolkit = toolkit
        self._setup(api_key, example_workflow)
    
    def _setup(self, api_key: str, example_workflow: Optional[str] = ""):
        instuctions = self.toolkit.get_tools_instructions
        sys_prompt = REACT_SYS_P.format(
            tools_and_role=instuctions,
            tool_names=self.toolkit.tool_names,
            example_workflow=example_workflow,
        )
        self.sys_prompt = sys_prompt
        self.llm = chat_from_key(
            api_key,
            sys_prompt=sys_prompt,
        )

    def _check_answer(self, ai_mssg:str) -> str:
        ai_mssg = re.sub(r'</?rules>', '', ai_mssg)
        if "SEARCH_ARTICLE" in ai_mssg:
           match = re.search(r'<([^<>]*)>', ai_mssg)
           if match:
              return match.group(1)
        return ""
    
    def __call__(
        self,
        user_query:str,
        max_iters: Optional[int] = 5,
        logging: Optional[bool] = False,
    ) -> str:
        next_prompt = user_query
        for _ in range(max_iters):
            if logging:
               print("\n")
            agent_response = self.step(next_prompt)

            if agent_response['Action'].lower() == 'finish':
                final_answer = agent_response['Final Answer']
                if logging:
                   print("\n")
                return final_answer
            
            if agent_response['Action'] not in self.toolkit.tool_names:
                raise Exception(f"Unknown action: {agent_response['Action']}")
            
            tool_result = self.toolkit(agent_response['Action'], agent_response['Action Input'])
    
            if len(tool_result) == 0 or tool_result == None:
                warnings.warn("Tool is giving no results (Rerunning the loop again) please check the tools")
            
            next_prompt = f"Thought: {agent_response['Thought']}\nAction: {agent_response['Action']}\nAction Input: {agent_response['Action Input']}\nObservation: {tool_result}"
            if logging:
                print(next_prompt)

        return "Max iterations reached without finding an answer."
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        parsed = {}
        current_key = None
        multiline_value = False

        for line in response.split('\n'):
            if ':' in line and not multiline_value:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key in ['Thought', 'Action', 'Action Input', 'Observation', 'Final Answer']:
                    current_key = key
                    if key == 'Action Input':
                        multiline_value = True
                        parsed[current_key] = value
                    else:
                        parsed[current_key] = value
            elif multiline_value and current_key == 'Action Input':
                parsed[current_key] += '\n' + line.strip()
                if line.strip().endswith('```'):
                    multiline_value = False
            elif current_key:
                parsed[current_key] += ' ' + line.strip()
        return parsed   
    
    def step(self, query:str) -> Dict[str, str]:
        response = self.llm(query)
        return self._parse_response(response)
    
    def parse(self, response: str):
        if ':' in response:
            key, value = response.split(':', 1)
