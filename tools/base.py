import abc
from typing import Optional, List
from typing import Dict
import inspect


SEP_LINE = f"""
{"-" * 100}
        """


INSTRUCT_LINE = """
tool_name: {name}
documentation:
            {doc}
            """

            
def has_multiple_arguments(func):
    sig = inspect.signature(func)
    parameters = sig.parameters
    return len(parameters) > 1


class BaseTool(abc.ABC):
    def __init__(
        self,
        tool_name:str,
        description:Optional[str]="",
    ):
        self.description = description
        self.tool_name = tool_name
    def __str__(self):
        desc = "Tool "
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
    def __repr__(self):
        desc = "Tool "
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError
    
    @property
    def get_doc(self):
        return self.__call__.__doc__


class ToolKit:
    def __init__(self, tools: Optional[List[BaseTool]] = []):
        self.name2tool = {}
        if len(tools):
            self.name2tool = {
                tool.tool_name: tool for tool in tools 
            }
        self.tools = tools    
        self.tool_names = ",".join([t.tool_name for t in tools])

    def _extract_json_str(self, json_str: str) -> Dict[str, str]:
        parsed = {}
        key = ""
        val = ""
        is_key = True 
        inside_quotes = False
        val_started = False
        for ch in json_str:
            if ch in ["'", '"']:
              inside_quotes = not inside_quotes
              if not inside_quotes and is_key and key:
                  is_key = False  
              elif not inside_quotes and not is_key and val_started:
                  is_key = True  
                  parsed[key.strip()] = val.strip().replace("\\n", "\n")
                  key = ""
                  val = ""
                  val_started = False
            elif inside_quotes:
                if is_key:
                    key += ch
                else:
                    val += ch
                    val_started = True
            else:
                if not is_key:
                    if ch in [":", " "]:  # Skip colon and space after key
                        continue
                    val += ch
                    val_started = True
        return parsed            

    def __getitem__(self, tool_idx):
        if isinstance(tool_idx, str):
           return self.name2tool[tool_idx]
        return self.tools[tool_idx]
    
    def __call__(self, tool_name: str, tool_inputs:str):
        tool_inputs = f"""{tool_inputs}"""
        tool = self.name2tool[tool_name]
        if has_multiple_arguments(tool):
          tool_inputs = eval(tool_inputs)
        else: 
          tool_inputs = self._extract_json_str(tool_inputs) 
        return  tool(**tool_inputs)   
    
    def append(self, tool):
        self.name2tool.update(
            {
                tool.tool_name:tool
            }
        )
        self.tools.append(tool)    
    
    @property
    def get_tools_instructions(self) -> str:
        line = SEP_LINE
        instructions = """"""
        for name, tool in self.name2tool.items():
            instruct = INSTRUCT_LINE.format(name=name, doc=tool.get_doc)
            instructions += instruct + line
        return instructions  

    def __str__(self) -> str:
        return f"[{self.tool_names}]"

    def __repr__(self) -> str:
        return f"[{self.tool_names}]"
