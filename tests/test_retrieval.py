from backend.rag.retriever import HybridRetriever


retriever = HybridRetriever("data/corpus")

results = retriever.search(
    "What is the cancellation policy?",
    top_k=3
)


for i, result in enumerate(results, start=1):

    print("\n==============================")
    print("RESULT", i)

    print(
        "SOURCE:",
        result["doc_id"],
        result["section"]
    )

    print(
        "SCORE:",
        result["score"]
    )

    print(
        result["text"][:500]
    )