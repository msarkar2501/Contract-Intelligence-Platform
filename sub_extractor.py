from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from system_prompts import EXTRACTOR_SYSTEM
from tool_list import EXTRACTION_TOOL

load_dotenv()
llm_client = OpenAI(
  api_key= os.environ["GEMINI_API_KEY"],
  base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def extraction_agent(contract_text):
    messages = [
        EXTRACTOR_SYSTEM,
        {"role": "user", "content": contract_text}
    ]

    response = llm_client.chat.completions.create(
        model = "gemini-3.6-flash",
        messages = messages,
        tools = [EXTRACTION_TOOL],
        tool_choice = {"type": "function", "function": {"name": "submit_extraction"}},
        max_tokens = 12000,
        reasoning_effort = "low"
    )

    if not response.choices[0].message.tool_calls:
        raise RuntimeError(
            f"extraction_agent: model did not return a tool call. \ncontent={response.choices[0].message.content!r}\nfinish reason = {response.choices[0].finish_reason!r}"
        )

    tool_call = response.choices[0].message.tool_calls[0]
    result = json.loads(tool_call.function.arguments)

    return result