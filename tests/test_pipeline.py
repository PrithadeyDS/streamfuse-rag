from backend.rag.pipeline import RAGEngine


engine = RAGEngine(
    "data/corpus"
)


session_id = "demo-session"


print("\n======================")
print("FIRST REQUEST")
print("======================")

result1 = engine.process(
    session_id,
    """
    Find a venue in Pune for 30 people
    and tell me the cancellation policy
    and catering options
    """
)

print("DECISION:", result1["decision"])
print("REFINEMENT:", result1["refinement"])
print("VERSION:", result1["version"])
print("QUERY:", result1["query"])

print("\nSUBQUERIES:")

for q in result1["subqueries"]:
    print("-", q)


print("\n======================")
print("LATE DETAIL")
print("======================")

result2 = engine.process(
    session_id,
    "Actually make that 50 people"
)

print("DECISION:", result2["decision"])
print("REFINEMENT:", result2["refinement"])
print("VERSION:", result2["version"])
print("QUERY:", result2["query"])


print("\n======================")
print("SUPPRESSION TEST")
print("======================")

result3 = engine.process(
    session_id,
    "Put that in bullet points"
)

print("DECISION:", result3["decision"])
print("VERSION:", result3["version"])