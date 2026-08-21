"""
Deterministic (non-LLM) check for clause types a contract of a given type would
normally be expected to have but weren't found. This is intentionally NOT an LLM
call — "what clauses does an NDA usually have" is stable domain knowledge, not
something that needs to be generated per request, so keeping it a plain lookup
makes this step free, instant, and fully unit-testable.

CONTRACT_TYPE_EXPECTATIONS is a starting heuristic based on common practice, not
legal advice — it's deliberately conservative (only flags clause types that are
genuinely standard for that contract type) and should be reviewed/extended by
someone with real contract-review experience before being relied on for actual
decisions.
"""

CONTRACT_TYPE_EXPECTATIONS = {
    "nda": {
        "confidentiality",
        "governing_law",
        "post_termination_obligations",
    },
    "msa": {
        "limitation_of_liability",
        "indemnification",
        "termination_for_cause",
        "governing_law",
        "confidentiality",
        "payment_terms",
        "warranties_and_disclaimers",
    },
    "consulting_agreement": {
        "payment_terms",
        "contract_term",
        "termination_for_cause",
        "governing_law",
        "assignment",
        "limitation_of_liability",
        "confidentiality",
    },
    "employment_agreement": {
        "payment_terms",
        "termination_for_cause",
        "confidentiality",
        "governing_law",
    },
    "licensing_agreement": {
        "ip_assignment",
        "payment_terms",
        "termination_for_cause",
        "limitation_of_liability",
        "governing_law",
    },
    "lease_agreement": {
        "payment_terms",
        "termination_for_cause",
        "contract_term",
        "governing_law",
    },
    "sales_agreement": {
        "payment_terms",
        "warranties_and_disclaimers",
        "limitation_of_liability",
        "governing_law",
    },
    "other": set(),
}


def check_missing_clauses(contract_type, found_clause_types):
    """
    contract_type: str, e.g. "nda" — from extraction_agent's output.
    found_clause_types: iterable of clause_type strings actually extracted.
    Returns a sorted list of clause_type strings that were expected but not found.
    """
    expected = CONTRACT_TYPE_EXPECTATIONS.get(contract_type, set())
    return sorted(expected - set(found_clause_types))
