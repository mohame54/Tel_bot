from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from dataclasses import dataclass
from typing import Optional


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
DB_URL = "https://chatbot-65def24.svc.gcp-starter.pinecone.io/"
SYS_P = "You are a helpful assistant which answers question based on some context if provided if the answer of the provided question is not presented in the context answer it briefly depending one your knowledge."


@dataclass
class ChatConfig:
    openai_api_key: str
    sys_prompt : Optional[str] = SYS_P
    temperature: Optional[float] = 0.7

    def unpack(self):
        return {k: getattr(self, k) for k in ["temperature", "openai_api_key"]}


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
      base =  ChatOpenAI(**self.config.unpack())
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


def chat_from_key(key):
    config  = ChatConfig(key)
    chat = ChatModel(config)   
    return chat
