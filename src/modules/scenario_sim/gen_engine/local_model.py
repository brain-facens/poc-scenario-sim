import os

from agents import OpenAIChatCompletionsModel
from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI

_ = load_dotenv(find_dotenv())

assert type(_model_name := os.getenv("LOCAL_MODEL")) is str
assert type(_model_url := os.getenv("LOCAL_URL")) is str
assert type(_key := os.getenv("OPENAI_KEY")) is str

_local_client: AsyncOpenAI = AsyncOpenAI(base_url=_model_url, api_key=_key)

model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=_model_name, openai_client=_local_client
)
