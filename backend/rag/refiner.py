import re


def is_refinement(text):
    text = text.lower().strip()

    refinement_phrases = [
        "actually",
        "instead",
        "change that",
        "make that",
        "update that",
        "rather",
        "instead make",
        "correction"
    ]

    return any(
        phrase in text
        for phrase in refinement_phrases
    )


def refine_query(previous_query, new_detail):
    if not previous_query:
        return new_detail

    new_detail_lower = new_detail.lower()

    # Example:
    # old: "venue in Pune for 30 people..."
    # new: "actually make that 50 people"
    number_match = re.search(
        r"\b(\d+)\s*(?:people|persons|attendees)?\b",
        new_detail_lower
    )

    if number_match:
        new_number = number_match.group(1)

        updated_query = re.sub(
            r"\b\d+\s*(people|persons|attendees)\b",
            f"{new_number} people",
            previous_query,
            count=1,
            flags=re.IGNORECASE
        )

        if updated_query != previous_query:
            return updated_query

    # General fallback
    return (
        previous_query.strip()
        + " "
        + new_detail.strip()
    )