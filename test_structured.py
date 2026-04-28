import os
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

class TestSchema(BaseModel):
    name: str = Field(..., description="The name of the user")
    age: int = Field(..., description="The age of the user")

model = init_chat_model(model="deepseek-chat", model_provider="openai", api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

try:
    print("Trying function_calling...")
    structured_model = model.with_structured_output(TestSchema, method="function_calling")
    res = structured_model.invoke("My name is John and I am 30 years old")
    print("Success:", res)
except Exception as e:
    print("Failed:", e)

try:
    print("Trying json_mode...")
    structured_model = model.with_structured_output(TestSchema, method="json_mode")
    res = structured_model.invoke("My name is Jane and I am 25 years old. Return in JSON format.")
    print("Success:", res)
except Exception as e:
    print("Failed:", e)
