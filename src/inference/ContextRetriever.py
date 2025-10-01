from typing import List, Tuple, Optional
from src.config import Config


class SimpleContextRetriever:
    def __init__(self, path: str = None, collection: str = None, embedding_model=None):
        self.path = path if path else Config.CHROMADB_PATH
        self.collection_name = collection if collection else Config.COLLECTION_NAME
        self.chroma_client = None
        self.collection = None
        self.embedding_model = embedding_model
        print(f"✅ ContextRetriever initialized (lazy loading)")

    def _initialize_chromadb(self) -> bool:
        """Lazy initialization of ChromaDB"""
        if self.chroma_client is None:
            try:
                import chromadb
                self.chroma_client = chromadb.PersistentClient(path=self.path)
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name
                )
                print(f"✅ ChromaDB initialized: {self.collection_name}")
            except Exception as e:
                print(f"❌ Failed to initialize ChromaDB: {e}")
                return False
        return True

    def _get_embedding_model(self):
        """Lazy load embedding model"""
        if self.embedding_model is None:
            try:
                self.embedding_model = Config.safe_get_embedding_model()
                if self.embedding_model is None:
                    print("❌ No embedding model available")
                    return None
            except Exception as e:
                print(f"❌ Error loading embedding model: {e}")
                return None
        return self.embedding_model

    def _apply_department_filter(self, dept: str) -> Optional[dict]:
        """Return a metadata filter dict or None."""
        if dept and dept.lower() != "general inquiry":
            return {"department": dept}
        return None

    def retrieve_context(
        self, query: str, dept: str, k: int = 10, max_docs: int = 5
    ) -> List[Tuple[str, float]]:
        try:
            # Ensure ChromaDB is ready
            if not self._initialize_chromadb():
                return []

            # Ensure embedding model is available
            model = self._get_embedding_model()
            if model is None:
                return []

            # Generate query embedding
            q_emb = model.encode(query, convert_to_tensor=False)
            filter_ = self._apply_department_filter(dept)

            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[q_emb],
                n_results=k,
                where=filter_,
            )

            docs = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            if not docs:
                return []

            # Pair (doc, distance, metadata) and sort ascending (closer first)
            filtered = sorted(
                zip(docs, distances, metadatas), key=lambda x: x[1]
            )

            # Docs with distance < 1
            top_filtered = [item for item in filtered if item[1] < 1]

            # Fallback if results are too few (< 1 doc within 1.5 distance)
            count_1_5 = sum(1 for item in filtered if item[1] < 1.5)
            if count_1_5 < 1:
                results = self.collection.query(
                    query_embeddings=[q_emb], n_results=k, where=None
                )
                docs = results.get("documents", [[]])[0]
                distances = results.get("distances", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]

                if not docs:
                    return []

                filtered = sorted(
                    zip(docs, distances, metadatas), key=lambda x: x[1]
                )
                top_filtered = [item for item in filtered if item[1] < 1]

            # Expand if top 2 docs share the same knowledge_id
            if len(filtered) >= 2:
                top_2_ids = []
                for i in range(min(2, len(filtered))):
                    metadata = filtered[i][2]
                    if metadata and "knowledge_id" in metadata:
                        top_2_ids.append(metadata["knowledge_id"])

                if len(set(top_2_ids)) == 1 and top_2_ids[0]:
                    knowledge_id = top_2_ids[0]
                    knowledge_filter = {"knowledge_id": knowledge_id}
                    if filter_:
                        knowledge_filter.update(filter_)

                    knowledge_results = self.collection.query(
                        query_embeddings=[q_emb],
                        n_results=k * 2,
                        where=knowledge_filter,
                    )

                    k_docs = knowledge_results.get("documents", [[]])[0]
                    k_distances = knowledge_results.get("distances", [[]])[0]
                    k_metadatas = knowledge_results.get("metadatas", [[]])[0]

                    if k_docs:
                        filtered = sorted(
                            zip(k_docs, k_distances, k_metadatas),
                            key=lambda x: x[1],
                        )
                        top_filtered = [item for item in filtered if item[1] < 1]

            # Ensure at least 4 docs (or fewer if not enough exist)
            if len(top_filtered) < 4:
                top_filtered = filtered[:max(4, min(len(filtered), max_docs))]
            else:
                top_filtered = top_filtered[:max_docs]

            # Return only (doc, distance)
            return [(item[0], item[1]) for item in top_filtered]

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
