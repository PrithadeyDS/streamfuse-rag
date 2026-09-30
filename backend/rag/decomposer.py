import re


def decompose_query(query):
    query = query.strip()

    parts = re.split(
        r"\b(?:and also|also|as well as|and)\b|[,;]",
        query,
        flags=re.IGNORECASE
    )

    subqueries = []

    for part in parts:
        part = part.strip()

        if len(part.split()) >= 3:
            subqueries.append(part)

    if not subqueries:
        subqueries = [query]

    return subqueries[:4]