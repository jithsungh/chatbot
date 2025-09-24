from typing import List
from sentence_transformers import SentenceTransformer, util
import chromadb
import numpy as np

class SimpleContextRetriever:
    def __init__(self, path = "./chromadb", collection = "TM-DOCS", embedding_model: SentenceTransformer = None):
        self.chroma_client = chromadb.PersistentClient(path=path)
        self.collection = self.chroma_client.get_or_create_collection(name=collection)
        self.embedding_model = embedding_model or SentenceTransformer("all-MiniLM-L6-v2")

    def _apply_department_filter(self, dept: str):
        """Return a metadata filter dict or None."""
        if dept and dept.lower() != "general inquiry":
            return {"department": dept}
        return None

    def retrieve_context(self, query: str, dept: str, k: int = 10, max_docs: int = 5) -> list[tuple]:
        try:
            q_emb = self.embedding_model.encode(query, convert_to_tensor=False)
            filter_ = self._apply_department_filter(dept)

            results = self.collection.query(
                query_embeddings=[q_emb],
                n_results=k,
                where=filter_
            )

            docs = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            if not docs:
                return []

            # Pair (doc, distance) and sort ascending (lower distance = closer)
            filtered = sorted(zip(docs, distances), key=lambda x: x[1])

            # return all docs with distance < 1
            top_filtered = [item for item in filtered if item[1] < 1]

            # ensure minimum 3 docs
            if len(top_filtered) < 3:
                # take first 3 from filtered (distance-sorted) regardless of distance
                top_filtered = filtered[:max(3, min(len(filtered), max_docs))]
            else:
                # limit to max_docs if more than allowed
                top_filtered = top_filtered[:max_docs]

            return top_filtered

        except Exception as e:
            print(f"❌ Context retrieval error: {e}")
            return []



# ------------------ Example usage ------------------x  

# def main():
#     retriever = SimpleContextRetriever()
    
#     while True:
#         query = input("Enter your query: ").strip()
#         if query.lower() in {"exit", "quit"}:
#             break
        
#         dept = input("Enter department (HR / IT / Security / General Inquiry): ").strip()
#         if not dept:
#             dept = "General Inquiry"
        
#         chunks = retriever.retrieve_context(query=query, dept=dept, k=10, max_docs=5)
        
#         print("\n--- Retrieved Chunks ---")
#         if chunks:
#             for i, (doc, score) in enumerate(chunks, 1):
#                 print(f"{i}-#####score: {score:.3f}######{doc}\n\n\n")
#         else:
#             print("No relevant chunks found.")
#         print()

# if __name__ == "__main__":
#     main()
