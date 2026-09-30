import time

from .controller import retrieval_decision
from .decomposer import decompose_query
from .retriever import HybridRetriever
from .session import SessionMemory
from .refiner import is_refinement, refine_query
from .generator import generate_grounded_answer


class RAGEngine:
    def __init__(self, corpus_dir):
        self.retriever = HybridRetriever(corpus_dir)
        self.memory = SessionMemory()


    def process(self, session_id, text):

        start_time = time.perf_counter()

        session = self.memory.get(session_id)

        if session is None:
            session = self.memory.create(session_id)


        # --------------------------------
        # CHECK IF THIS IS A REFINEMENT
        # --------------------------------

        refinement = False

        if session["query"] and is_refinement(text):

            refinement = True

            final_query = refine_query(
                session["query"],
                text
            )

        else:
            final_query = text


        # --------------------------------
        # RETRIEVAL DECISION
        # --------------------------------

        decision = retrieval_decision(
            text,
            has_previous_answer=bool(
               session["query"] or session["evidence"]
            )
        )  


        # --------------------------------
        # WAIT
        # --------------------------------

        if decision == "WAIT":

            return {
                "decision": "WAIT",
                "refinement": refinement,
                "query": final_query,
                "subqueries": [],
                "evidence": [],
                "citations": [],
                "version": session["version"],
                "metrics": {
                    "retrieval_ms": 0,
                    "total_ms": 0
                }
            }


        # --------------------------------
        # SUPPRESS
        # --------------------------------

        if decision == "SUPPRESS":

            return {
                "decision": "SUPPRESS",
                "refinement": False,
                "query": session["query"],
                "subqueries": [],
                "evidence": session["evidence"],
                "citations": session["citations"],
                "version": session["version"],
                "metrics": {
                    "retrieval_ms": 0,
                    "total_ms": 0
                }
            }


        # --------------------------------
        # DECOMPOSE
        # --------------------------------

        subqueries = decompose_query(
            final_query
        )


        # --------------------------------
        # RETRIEVE
        # --------------------------------

        retrieval_start = time.perf_counter()

        all_evidence = []

        for subquery in subqueries:

            results = self.retriever.search(
                subquery,
                top_k=3
            )

            for result in results:
                result["subquery"] = subquery
                all_evidence.append(result)


        # --------------------------------
        # DEDUPLICATE
        # --------------------------------

        unique_evidence = []

        seen = set()

        for evidence in all_evidence:

            key = (
                evidence["doc_id"],
                evidence["section"],
                evidence["text"]
            )

            if key not in seen:

                seen.add(key)

                unique_evidence.append(
                    evidence
                )


        unique_evidence = sorted(
            unique_evidence,
            key=lambda x: x["score"],
            reverse=True
        )[:6]


        # --------------------------------
        # CITATIONS
        # --------------------------------

        citations = []

        for evidence in unique_evidence:

            citations.append({
                "doc_id": evidence["doc_id"],
                "section": evidence["section"]
            })


        retrieval_end = time.perf_counter()

          # --------------------------------
        # GROUNDED ANSWER
        # --------------------------------

        generated = generate_grounded_answer(
            final_query,
            unique_evidence
        )

        answer = generated["answer"]

        # --------------------------------
        # UPDATE SESSION
        # --------------------------------

        session = self.memory.update(
            session_id=session_id,
            query=final_query,
            answer=answer,
            evidence=unique_evidence,
            citations=citations
        )


        total_end = time.perf_counter()


        return {

            "decision": "RETRIEVE",

            "refinement": refinement,

            "query": final_query,
            
            "answer": answer,

            "subqueries": subqueries,

            "evidence": unique_evidence,

            "citations": citations,

            "version": session["version"],

            "metrics": {

                "retrieval_ms": round(
                    (retrieval_end - retrieval_start)
                    * 1000,
                    2
                ),

                "total_ms": round(
                    (total_end - start_time)
                    * 1000,
                    2
                )
            }
        }