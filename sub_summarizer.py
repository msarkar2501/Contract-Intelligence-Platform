from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from system_prompts import SUMMARY_SYSTEM
from tool_list import SUMMARY_TOOL

load_dotenv()
llm_client = OpenAI(
    api_key= os.environ["GEMINI_API_KEY"],
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

def summary_agent(contract_type, party_role, extracted_clauses, risk_assessments, missing_clauses):
    combined_output = json.dumps({
        "contract_type": contract_type,
        "party_role": party_role or "unspecified",
        "clauses": extracted_clauses,
        "risk_assessments": risk_assessments,
        "missing_clauses": missing_clauses,
    })
    summarized_messages = [
        SUMMARY_SYSTEM,
        {"role": "user", "content": combined_output}
    ]

    response = llm_client.chat.completions.create(
        model = "gemini-3.6-flash",
        messages = summarized_messages,
        tools = [SUMMARY_TOOL],
        tool_choice = {"type": "function", "function": {"name": "submit_summary"}},
        max_tokens = 8000,
        reasoning_effort = "low"
    )

    choice = response.choices[0]

    if not choice.message.tool_calls:
        raise RuntimeError(
            f"summary_agent: model did not return a tool call. "
            f"finish_reason={choice.finish_reason!r} content={choice.message.content!r}"
        )

    tool_call = choice.message.tool_calls[0]
    result = json.loads(tool_call.function.arguments)

    return result