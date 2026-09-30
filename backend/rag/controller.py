def retrieval_decision(text, has_previous_answer=False):
    text = text.strip().lower()

    if not text:
        return "WAIT"

    # --------------------------------
    # SUPPRESS
    # User only wants existing result
    # transformed / reformatted
    # --------------------------------

    suppression_phrases = [
        "make it shorter",
        "summarize that",
        "summarise that",
        "put that in bullet points",
        "make that bullet points",
        "bullet points",
        "repeat that",
        "rephrase that",
        "rewrite that",
        "format that",
        "make it concise"
    ]

    if has_previous_answer:
        for phrase in suppression_phrases:
            if phrase in text:
                return "SUPPRESS"

    # --------------------------------
    # WAIT
    # Utterance may still be incomplete
    # --------------------------------

    words = text.split()

    if len(words) < 5:
        return "WAIT"

    # --------------------------------
    # Otherwise retrieve
    # --------------------------------

    return "RETRIEVE"