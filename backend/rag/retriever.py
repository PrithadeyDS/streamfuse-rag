from pathlib import Path

import numpy as np
from pypdf import PdfReader
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


class HybridRetriever:
    def __init__(self, corpus_dir):
        self.corpus_dir = Path(corpus_dir)
        self.chunks = []

        print("Loading corpus...")
        self._load_corpus()

        if not self.chunks:
            raise ValueError(
                f"No readable documents found inside {self.corpus_dir}"
            )

        print(f"Loaded {len(self.chunks)} chunks.")

        texts = [chunk["text"] for chunk in self.chunks]

        # Sparse / lexical index
        self.tokenized_corpus = [
            text.lower().split()
            for text in texts
        ]

        self.bm25 = BM25Okapi(self.tokenized_corpus)

        # Dense / semantic model
        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Creating embeddings...")

        self.embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        print("Retriever ready.")


    def _add_chunks(self, text, doc_id, section):
        chunk_size = 700
        overlap = 100

        start = 0
        chunk_number = 0

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if len(chunk_text) > 40:
                self.chunks.append({
                    "text": chunk_text,
                    "doc_id": doc_id,
                    "section": section,
                    "chunk": chunk_number
                })

            chunk_number += 1

            start += chunk_size - overlap


    def _load_corpus(self):
        if not self.corpus_dir.exists():
            raise ValueError(
                f"Corpus directory does not exist: {self.corpus_dir}"
            )

        for path in self.corpus_dir.glob("*"):

            suffix = path.suffix.lower()

            if suffix == ".pdf":
                reader = PdfReader(path)

                for page_number, page in enumerate(
                    reader.pages,
                    start=1
                ):
                    text = page.extract_text() or ""

                    self._add_chunks(
                        text=text,
                        doc_id=path.stem,
                        section=f"page_{page_number}"
                    )

            elif suffix in [".txt", ".md"]:

                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                self._add_chunks(
                    text=text,
                    doc_id=path.stem,
                    section="document"
                )


    def search(self, query, top_k=5):

        # -------------------------
        # BM25 sparse retrieval
        # -------------------------

        query_tokens = query.lower().split()

        bm25_scores = self.bm25.get_scores(
            query_tokens
        )

        sparse_ranking = np.argsort(
            bm25_scores
        )[::-1]


        # -------------------------
        # Dense semantic retrieval
        # -------------------------

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        dense_scores = np.dot(
            self.embeddings,
            query_embedding
        )

        dense_ranking = np.argsort(
            dense_scores
        )[::-1]


        # -------------------------
        # Reciprocal Rank Fusion
        # -------------------------

        rrf_scores = {}

        RRF_K = 60

        for rank, index in enumerate(dense_ranking):

            rrf_scores[index] = (
                rrf_scores.get(index, 0)
                + 1 / (RRF_K + rank + 1)
            )


        for rank, index in enumerate(sparse_ranking):

            rrf_scores[index] = (
                rrf_scores.get(index, 0)
                + 1 / (RRF_K + rank + 1)
            )


        final_ranking = sorted(
            rrf_scores.items(),
            key=lambda item: item[1],
            reverse=True
        )


        # -------------------------
        # Return best evidence
        # -------------------------

        results = []

        for index, score in final_ranking[:top_k]:

            chunk = self.chunks[index]

            results.append({
                "text": chunk["text"],
                "doc_id": chunk["doc_id"],
                "section": chunk["section"],
                "chunk": chunk["chunk"],
                "score": round(float(score), 6)
            })

        return results