from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from dataclasses import dataclass
from typing import Optional
import requests


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
HF_TOKEN = "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"
DB_TOKEN = "49b4854e-dddd-435a-b30c-bb662622e213"
DB_URL = "https://chatbot-65def24.svc.gcp-starter.pinecone.io/"
SYS_P = "You are a helpful assistant which answers question based on some context if provided if the answer of the provided question is not presented in the context answer it briefly depending one your knowledge."


@dataclass
class ChatConfig:
    sys_prompt : Optional[str] = SYS_P
    temperature: Optional[float] = 0.7
    openai_api_key: Optional[str] = "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"

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

  def invoke_chain(self, question: str, num_docs: Optional[int] = 1):
      res = query_db(question, num_docs=num_docs).json()['matches']
      texts = []
      for i, meta in enumerate(res):
         text = meta['metadata']['text']
         texts.append(text)
      text = "\n".join(texts)
      context_question = f"based on <{text}\n> answer the following: {question}"
      return self.invoke(context_question)

  def invoke(self, question: str):
      self.history.add_user_message(question)   
      ai_message = self.base.invoke(
          {
              "messages":self.history.messages
          }
      ).content
      self.history.add_ai_message(ai_message)
      return ai_message


def query_texts_vectors(
    texts,
):
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_ID}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options":{"wait_for_model":True}})
    return response.json()


def query_db(text, num_docs=1, include_metadata=True):
    embd = query_texts_vectors(text)
    if include_metadata:
        include_metadata = "true"
    else:
        include_metadata = "false"
    body_obj = {
        "includeValues":"false",
        "includeMetadata":include_metadata,
        "topK":num_docs,
        "vector":embd,
    }
    headers = {"Content-Type":"application/json"
               ,"Accept":"application/json", "Api-Key":DB_TOKEN}
    url = DB_URL + "query"
    res = requests.post(url, headers=headers, json=body_obj)
    return res

def chat_from_sys(prompt):
    config  = ChatConfig(prompt)
    chat = ChatModel(config)   
    return chat