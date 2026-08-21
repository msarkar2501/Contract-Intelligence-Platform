import json
from sub_extractor import extraction_agent
from sub_validation import validation_agent
from sub_risk_flagging import risk_agent
from sub_summarizer import summary_agent
from sub_gap_checker import check_missing_clauses
from pypdf import PdfReader

path = "contract.pdf"

def load_pdf(filepath):
    reader = PdfReader(filepath)
    full_text = ""

    for page in reader.pages:
        full_text += page.extract_text() or ""  # extract_text() can return None on image-only pages

    print(f"[load_pdf] extracted {len(full_text)} characters")
    return full_text


def extract_step(contract_text):
    """
    Party role introduces perspective on whose side is much riskier.
    """
    print("[extract_step] calling extraction_agent...")
    extracted_result = extraction_agent(contract_text)
    print(f"[extract_step] contract_type={extracted_result.get('contract_type')}, "
          f"is_contract={extracted_result['is_contract']}")

    if not extracted_result["is_contract"]:
        return extracted_result

    for i, clause in enumerate(extracted_result["clauses"]):
        clause["clause_id"] = i
    print(f"[extract_step] {len(extracted_result['clauses'])} clauses, "
          f"{len(extracted_result.get('parties', []))} parties extracted")

    return extracted_result


def analyze_step(contract_text, extracted_result, party_role=None):
    """
    Phase 2: validation, perspective-aware risk assessment, gap check, and summary.
    Call this after the user has picked party_role from extracted_result["parties"]
    (or leave it as None to fall back to the "unspecified" default behavior).
    """
    validated_clauses, flagged_clauses = validation_agent(extracted_result["clauses"], contract_text)
    print(f"[analyze_step] validated: {len(validated_clauses)}, flagged: {len(flagged_clauses)}")

    risk_assessments = risk_agent(validated_clauses, party_role)
    print(f"[analyze_step] {len(risk_assessments)} risk assessments returned")

    found_types = {c["clause_type"] for c in validated_clauses} | {c["clause_type"] for c in flagged_clauses}
    missing_clauses = check_missing_clauses(extracted_result.get("contract_type", "other"), found_types)
    print(f"[analyze_step] missing_clauses: {missing_clauses}")

    summary = summary_agent(
        extracted_result.get("contract_type", "other"),
        party_role,
        validated_clauses,
        risk_assessments,
        missing_clauses,
    )
    print("[analyze_step] summary generated")

    return {
        "is_contract": True,
        "contract_type": extracted_result.get("contract_type", "other"),
        "party_role": party_role or "unspecified",
        "parties": extracted_result.get("parties", []),
        "summary": summary,
        "clauses": validated_clauses,
        "risks": risk_assessments,
        "missing_clauses": missing_clauses,
        "flagged_by_validation": flagged_clauses,
    }


def orchestrator(contract_text, party_role=None):
    """
    Single-call convenience wrapper for CLI/testing — runs both phases back to back.
    The Streamlit app should call extract_step() and analyze_step() separately instead,
    so it can show the user the detected parties before asking which one they are.
    """
    extracted_result = extract_step(contract_text)

    if not extracted_result["is_contract"]:
        return {"is_contract": False, "message": "This doesn't appear to be a contract."}

    return analyze_step(contract_text, extracted_result, party_role)


if __name__ == "__main__":
    result = orchestrator(load_pdf(path))
    print(json.dumps(result, indent=2, default=str))