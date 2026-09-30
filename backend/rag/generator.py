import re


def _split_sentences(text):
    sentences = re.split(
        r'(?<=[.!?])\s+',
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _keywords(text):
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were",
        "in", "on", "at", "to", "for", "of", "and",
        "or", "with", "me", "my", "that", "this",
        "tell", "find", "need", "please"
    }

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in stopwords
        and len(word) > 2
    }


def generate_grounded_answer(query, evidence):

    if not evidence:
        return {
            "answer":
            "I could not verify an answer from the available corpus.",
            "sources": []
        }

    query_keywords = _keywords(query)

    candidate_sentences = []

    for item in evidence:

        sentences = _split_sentences(
            item["text"]
        )

        for sentence in sentences:

            sentence_keywords = _keywords(
                sentence
            )

            overlap = len(
                query_keywords
                & sentence_keywords
            )

            candidate_sentences.append({
                "sentence": sentence,
                "score": overlap,
                "doc_id": item["doc_id"],
                "section": item["section"]
            })


    # Prefer sentences matching the query
    candidate_sentences.sort(
        key=lambda x: x["score"],
        reverse=True
    )


    selected = []
    seen_sentences = set()

    for item in candidate_sentences:

        normalized = item[
            "sentence"
        ].lower()

        if normalized in seen_sentences:
            continue

        seen_sentences.add(
            normalized
        )

        selected.append(item)

        if len(selected) == 5:
            break


    if not selected:
        return {
            "answer":
            "I could not verify an answer from the available corpus.",
            "sources": []
        }


    answer_lines = []

    sources = []

    for item in selected:

        citation = (
            f'[{item["doc_id"]} '
            f'{item["section"]}]'
        )

        answer_lines.append(
            f'- {item["sentence"]} {citation}'
        )

        source = {
            "doc_id": item["doc_id"],
            "section": item["section"]
        }

        if source not in sources:
            sources.append(source)


    answer = (
        "Based on the available corpus:\n\n"
        + "\n".join(answer_lines)
    )


    return {
        "answer": answer,
        "sources": sources
    }