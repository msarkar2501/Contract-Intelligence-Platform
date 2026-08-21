from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from system_prompts import RISK_SYSTEM
from tool_list import RISK_TOOL

load_dotenv()

llm_client = OpenAI(
    api_key= os.environ["GEMINI_API_KEY"],
    base_url= "https://generativelanguage.googleapis.com/v1beta/openai/"
)

def risk_agent(clauses, party_role=None):
    payload = {
        "party_role": party_role or "unspecified",
        "clauses": clauses,
    }
    risk_messages = [
        RISK_SYSTEM,
        {"role": "user", "content": json.dumps(payload)}
    ]

    riskponse = llm_client.chat.completions.create(
        model = "gemini-3.6-flash",
        messages = risk_messages,
        tools = [RISK_TOOL],
        tool_choice = {"type": "function", "function": {"name": "submit_risk_assessment"}},
        max_tokens = 12000,
        reasoning_effort = "low"
    )

    if not riskponse.choices[0].message.tool_calls:
        raise RuntimeError(
            f"risk_agent: model did not return a tool call. content={riskponse.choices[0].message.content!r}\nfinish reason={riskponse.choices[0].finish_reason!r}"
        )

    risk_tool_call = riskponse.choices[0].message.tool_calls[0]
    riskult = json.loads(risk_tool_call.function.arguments)

    return riskult["assessments"]