from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
  api_key= os.environ["GEMINI_API_KEY"],
  base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

models = client.models.list()
for m in models:
    print(m.id)