from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from langchain.memory import ChatMessageHistory
from dataclasses import dataclass
from typing import Optional
import os


EMBEDDING_ID = "sentence-transformers/all-MiniLM-L6-v2"
DB_URL = "https://chatbot-65def24.svc.gcp-starter.pinecone.io/"


SYS_P = """You are a helpful Ai assistant which answers questions based on user quries,
if your don't have the sufficient knowledge to answer you should answer only with a proper keyword with specified parameters seperated between the two angle brackets according to the rules given please follow them carefully
<rules>
SEARCH_ARTICLE<article_subject>: if the user enters a prompt and you need some knowledge to asses your answer, article_subject: refers to the wanted article subject that the user asked about.
GENERATE_CODE<code_docs>: if the user enters a prompt that asks you to write code and you are not sure about some certain libraries and need some docummentation to asses your knowledge for generating code, code_docs: refers to the required code documentations to generate user wanted code could be multiple names seperated by a comma.
SAVE_CODE <script_name>: if the user asks you to generate code and you have the sufficient knowledge to do so, script_name: referes to conventional name for the wanted code.
</rules>
REMEMBER:
  If the knowledge is provided for you somehow including from the user side this should be sufficient for you to generate an answer.
if you do have the knowledge you don't have to follow the rules and give a clear and concise answer unless the user asks you to generate code then you should follow the above rules.
"""


@dataclass
class ChatConfig:
    sys_prompt : Optional[str] = SYS_P
    model: Optional[str] = "gemini-1.5-flash"
    temperature: Optional[float] = 0.7
    safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }


    def unpack(self):
        return {k: getattr(self, k) for k in ["temperature", "model", "safety_settings"]}


class ChatModel:
  def __init__(self, config: ChatConfig, description=""):
      self.config = config
      self.description = description
      self.history = ChatMessageHistory()
      self.setup()

  def setup(self):
      sys_prompt =  self.config.sys_prompt
      prompt = ChatPromptTemplate.from_messages(
        [(
            "system",
            sys_prompt,
        ),
        MessagesPlaceholder(variable_name="messages"),]
      )
      base =  ChatGoogleGenerativeAI(**self.config.unpack())
      self.base = prompt | base 

  def _trim_messages(self, length: int, last: bool=True):
      stored_mssgs = self.history.messages
      stored_mssgs = stored_mssgs[length:] if last else stored_mssgs[:length]
      self.history.clear()
      for message in stored_mssgs:
            self.history.add_message(message)

  def __call__(self, question: str, save_hist: bool=True):
      self.history.add_user_message(question)   
      ai_message = self.base.invoke(
          {
            "messages":self.history.messages
          }
      ).content
      self.history.add_ai_message(ai_message)
      if not save_hist:
         self._trim_messages(-2, False)

      return ai_message
  
  def __str__(self):
        desc = "LLM"
        if self.description != "":
            desc = desc + f"for:{self.description}"
        return desc
    
  def __repr__(self):
      desc = "LLM"
      if self.description != "":
        desc = desc + f"for:{self.description}"
      return desc


def chat_from_key(api_key,**kwargs):
    os.environ['GOOGLE_API_KEY'] = api_key
    config  = ChatConfig(
        **kwargs,
    )
    chat = ChatModel(config)   
    return chat
