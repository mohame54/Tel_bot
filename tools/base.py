import abc
from typing import Optional, List

SEP_LINE = f"""
{"-" * 100}
        """


INSTRUCT_LINE = """
tool_name: {name}
documentation:
            {doc}
            """


class BaseTool(abc.ABC):
    def __init__(
        self,
        tool_name:str,
        description:Optional[str]="",
    ):
        self.description = description
        self.tool_name = tool_name
    def __str__(self):
        desc = "Tool"
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
    def __repr__(self):
        desc = "Tool"
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

    def __getitem__(self, tool_idx):
        if isinstance(tool_idx, str):
           return self.name2tool[tool_idx]
        return self.tools[tool_idx]
    
    def __call__(self, tool_name: str, *toolArgs, **toolKwargs):
        return self.name2tool[tool_name](*toolArgs, **toolKwargs)
    
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
            instruct = INSTRUCT_LINE.format(name, tool.get_doc)
            instructions += instruct + line
        return instructions   
