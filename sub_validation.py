from rapidfuzz import fuzz

def validation_agent(clauses, contract_text, threshold = 80):
    validated_clauses = []
    flagged_clauses = []

    for clause in clauses:
        score = fuzz.partial_ratio(clause['clause_text'], contract_text)

        if score >= threshold:
            validated_clauses.append(clause)
        else:
            clause["validation_score"] = score
            flagged_clauses.append(clause)

    return validated_clauses, flagged_clauses