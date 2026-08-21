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
   - risk_level: A string indicating the risk level assigned to the clause (low, medium, high).
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
                            "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                            "reasoning": {
                                "type": "string",
                                "description": "One or two sentence explanation for the assigned risk level, relative to party_role."
                            }
                        },
                        "required": ["clause_id", "clause_type", "section_reference", "risk_level", "reasoning"]
                    }
                }
            },
            "required": ["assessments"]
        }
    }
}