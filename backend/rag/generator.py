def generate_grounded_answer(query, evidence):
    if not evidence:
        return {
            "answer": "I could not verify an answer from the available corpus.",
            "sources": []
        }

    answer_parts = []
    sources = []

    for item in evidence[:4]:
        text = item["text"].strip()

        source_label = f'{item["doc_id"]} - {item["section"]}'

        answer_parts.append(
            f"{text} [{source_label}]"
        )

        sources.append({
            "doc_id": item["doc_id"],
            "section": item["section"]
        })

    answer = " ".join(answer_parts)

    return {
        "answer": answer,
        "sources": sources
    }