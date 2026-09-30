import time

from backend.rag.pipeline import RAGEngine


engine = RAGEngine("data/corpus")


tests = [
    {
        "name": "Incomplete utterance",
        "session": "bench-1",
        "text": "I need to plan",
        "expected": "WAIT"
    },
    {
        "name": "Normal retrieval",
        "session": "bench-2",
        "text": "Find a venue in Pune for 30 people",
        "expected": "RETRIEVE"
    },
    {
        "name": "Multi-intent retrieval",
        "session": "bench-3",
        "text": "Find a venue in Pune for 30 people and tell me the cancellation policy and catering options",
        "expected": "RETRIEVE"
    },
]


passed = 0
latencies = []


print("\nSTREAMFUSE BENCHMARK")
print("=" * 50)


for test in tests:

    start = time.perf_counter()

    result = engine.process(
        test["session"],
        test["text"]
    )

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    latencies.append(elapsed)

    success = (
        result["decision"]
        == test["expected"]
    )

    if success:
        passed += 1

    print("\nTEST:", test["name"])
    print("Expected:", test["expected"])
    print("Actual:", result["decision"])
    print("Passed:", success)
    print("Latency:", round(elapsed, 2), "ms")


# -----------------------------
# Refinement test
# -----------------------------

session_id = "bench-refine"

engine.process(
    session_id,
    "Find a venue in Pune for 30 people and tell me the cancellation policy"
)

refined = engine.process(
    session_id,
    "Actually make that 50 people"
)

refinement_success = (
    refined["refinement"] is True
    and "50 people" in refined["query"]
)

print("\nTEST: Session refinement")
print("Expected: 30 → 50 people")
print("Actual:", refined["query"])
print("Passed:", refinement_success)

if refinement_success:
    passed += 1


# -----------------------------
# Suppression test
# -----------------------------

suppressed = engine.process(
    session_id,
    "Put that in bullet points"
)

suppression_success = (
    suppressed["decision"]
    == "SUPPRESS"
)

print("\nTEST: Retrieval suppression")
print("Expected: SUPPRESS")
print("Actual:", suppressed["decision"])
print("Passed:", suppression_success)

if suppression_success:
    passed += 1


total_tests = 5

accuracy = (
    passed / total_tests
) * 100

average_latency = (
    sum(latencies)
    / len(latencies)
)


print("\n" + "=" * 50)
print("FINAL RESULTS")
print("=" * 50)

print(
    f"Behavior tests passed: "
    f"{passed}/{total_tests}"
)

print(
    f"Behavior accuracy: "
    f"{accuracy:.1f}%"
)

print(
    f"Average processing latency: "
    f"{average_latency:.2f} ms"
)