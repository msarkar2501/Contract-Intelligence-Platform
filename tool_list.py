from system_prompts import CLAUSE_DESCRIPTIONS, CONTRACT_TYPES

"""
submit_extraction function is used to submit the structured list of clauses extracted from a contract.
Parameters:
1. is_contract: A boolean indicating whether the provided file is a contract or not.
2. contract_type: Best-matching contract category (see CONTRACT_TYPES in system_prompts.py).
3. parties: Every distinct party to the agreement, with their real name and the shorthand
   the contract itself uses for them.
4. clauses: An array of objects, each representing a clause extracted from the contract. Each object contains:
   - clause_type: The type of clause (see CLAUSE_DESCRIPTIONS in system_prompts.py)
   - clause_text: The verbatim text of the clause, copied exactly from the contract.
   - section_reference: The section or clause number as written in the contract, or an empty string if none.
   - key_terms: A plain-text note of extracted specifics such as dollar amounts, notice periods, dates, percentages, etc.
"""

EXTRACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_extraction",
        "description": "Submit the structured list of clauses extracted from the contract.",
        "parameters": {
            "type": "object",
            "properties": {
                "is_contract": {
                    "type": "boolean",
                    "description": "True if it is a contract, false otherwise."
                },
                "contract_type": {
                    "type": "string",
                    "enum": list(CONTRACT_TYPES.keys()),
                    "description": "Best-matching contract category."
                },
                "parties": {
                    "type": "array",
                    "description": "Every distinct party to the agreement. Empty array if is_contract is false.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The party's actual name as written in the contract."
                            },
                            "role_label": {
                                "type": "string",
                                "description": "How the contract refers to this party, e.g. 'Company', 'Consultant'."
                            }
                        },
                        "required": ["name", "role_label"]
                    }
                },
                "clauses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "clause_type": {
                                "type": "string",
                                "enum": list(CLAUSE_DESCRIPTIONS.keys())
                            },
                            "clause_text": {
                                "type": "string",
                                "description": "Verbatim text of the clause, copied exactly from the contract."
                            },
                            "section_reference": {
                                "type": "string",
                                "description": "Section/clause number as written in the contract, or empty string if none."
                            },
                            "key_terms": {
                                "type": "string",
                                "description": "Plain-text note of extracted specifics: dollar amounts, notice periods, dates, percentages."
                            }
                        },
                        "required": ["clause_type", "clause_text", "section_reference", "key_terms"]
                    }
                }
            },
            "required": ["is_contract", "contract_type", "parties", "clauses"]
        }
    }
}

# =========================================================================================================================================================

"""
submit_risk_assessment function is used to submit a risk rating for each clause extracted from a contract.
The function takes a single parameter:
1. assessments: An array of objects, each representing a clause and its associated risk assessment. Each object contains:
   - clause_type: The type of clause (e.g., indemnification, limitation_of_liability, termination, etc.)
   - section_reference: The section or clause number as written in the contract, or an empty string if none.
   - risk_score: A string indicating the risk score assigned to the clause (negligible:1::severe:10).
   - reasoning: A one or two sentence explanation for the assigned risk level, relative to the party_role
     the assessment was done for.
"""

RISK_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_risk_assessment",
        "description": "Submit a risk rating for each clause.",
        "parameters": {
            "type": "object",
            "properties": {
                "assessments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "clause_id": {
                                "type": "integer",
                                "description": "The clause_id given to this clause. Copy it back exactly — do not renumber or invent one."
                            },
                            "clause_type": {
                                "type": "string",
                                "enum": list(CLAUSE_DESCRIPTIONS.keys())
                            },
                            "section_reference": {"type": "string"},
                            "risk_score": {"type": "integer", 
                                           "minimum": 1,
                                           "maximum": 10,
                                           "description": "How much this clause burdens or exposes party_role, from 1 (negligible) to 10 (severe)."
                                           },
                            "reasoning": {
                                "type": "string",
                                "description": "One or two sentence explanation for the assigned risk score, relative to party_role."
                            }
                        },
                        "required": ["clause_id", "clause_type", "section_reference", "risk_score", "reasoning"]
                    }
                }
            },
            "required": ["assessments"]
        }
    }
}

# ========================================================================================================================================================

"""
submit_summary function is used to submit the structured summary of a contract analysis.
Parameters:
1. summary_text: Plain-English narrative covering contract type, parties, whose perspective
   the analysis reflects, the 2-4 highest risk_score findings (named with their scores),
   and a note on any missing_clauses that plausibly matter.
2. overall_risk_score: A single integer 1-10 rating for the contract as a whole, weighted
   toward the most severe finding(s) present rather than a plain average.
3. overall_risk_explanation: One or two sentence explanation of the overall_risk_score.
"""

SUMMARY_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_summary",
        "description": "Submit the structured summary and overall risk score for a contract analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary_text": {
                    "type": "string",
                    "description": "Plain-English narrative covering contract type, parties, "
                                    "whose perspective the analysis reflects, the highest "
                                    "risk_score findings named with their scores, and any "
                                    "notable missing_clauses. Do not restate the overall score here."
                },
                "overall_risk_score": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Overall risk to party_role from this contract as a whole, "
                                    "1 (negligible) to 10 (severe). Weighted toward the most "
                                    "severe individual finding(s), not a plain average of all "
                                    "clause risk_scores. Missing_clauses should push this up "
                                    "even though they have no risk_score of their own."
                },
                "overall_risk_explanation": {
                    "type": "string",
                    "description": "One or two sentence explanation of why overall_risk_score "
                                    "was assigned, referencing the specific finding(s) or gaps "
                                    "that drove it."
                }
            },
            "required": ["summary_text", "overall_risk_score", "overall_risk_explanation"]
        }
    }
}