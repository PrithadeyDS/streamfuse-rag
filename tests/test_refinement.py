from backend.rag.refiner import (
    is_refinement,
    refine_query
)


previous = """
Find a venue in Pune for 30 people
and tell me the cancellation policy
and catering options
"""


new_detail = "Actually make that 50 people"


print("IS REFINEMENT:")
print(is_refinement(new_detail))


print("\nOLD QUERY:")
print(previous)


updated = refine_query(
    previous,
    new_detail
)


print("\nUPDATED QUERY:")
print(updated)