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


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
DB_URL = "https://chatbot-65def24.svc.gcp-starter.pinecone.io/"


SYS_P = """You are a helpful Ai assistant which answers questions based on user quries,
if your don't have the sufficient knowledge to answer you should answer only with a proper keywords according to the rules given please follow them carefully
<rules>
SEARCH_ARTICLE: if the user enters a prompt and you need some knowledge to asses your answer.
GENERATE_CODE: if the user enters a prompt that asks you to write code and you are not sure about some certain libraries and need some docummentation to asses your knowledge for generating code.
</rules>
REMEMBER:
  If the knowledge is provided for you somehow including from the user side this should be sufficient for you to generate an answer
if you do have the knowledge you don't follow the rules and give a clear and concise answer.
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
  def __init__(self, config: ChatConfig):
      self.config = config
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

  def invoke(self, question: str):
      self.history.add_user_message(question)   
      ai_message = self.base.invoke(
          {
            "messages":self.history.messages
          }
      ).content
      self.history.add_ai_message(ai_message)
      return ai_message


def chat_from_key(api_key,**kwargs):
    os.environ['GOOGLE_API_KEY'] = api_key
    config  = ChatConfig(
        api_key=api_key,
        **kwargs,
    )
    chat = ChatModel(config)   
    return chat
