from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from system_prompts import SUMMARY_SYSTEM

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
        max_tokens = 8000,
        reasoning_effort = "low"
    )

    summary = response.choices[0].message.content

    if not summary:
        raise RuntimeError(
            f"summary_agent: model returned empty content. "
            f"finish_reason={response.choices[0].finish_reason!r}"
        )

    return summary