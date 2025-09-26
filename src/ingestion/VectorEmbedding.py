import uuid
from typing import List, Any
from src.config import Config

def get_collection():
    """Get the shared ChromaDB collection (lazy loaded)"""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
        collection = client.get_or_create_collection(name=Config.COLLECTION_NAME)
        return collection
    except Exception as e:
        print(f"❌ Error creating ChromaDB collection: {e}")
        return None

def vector_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for texts using shared model (lazy loaded)"""
    try:
        from src.config import Config
        model = Config.safe_get_embedding_model()
        
        if model is None:
            print("❌ No embedding model available")
            return []
            
        embeddings = model.encode(texts)
        if not isinstance(embeddings, list):
            embeddings = embeddings.tolist()
        return embeddings
        
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return []

def get_data(chunks: List[Any]) -> tuple:
    """Extract texts and metadata from document chunks"""
    try:
        texts = [doc.page_content for doc in chunks]
        metadatas = [doc.metadata for doc in chunks]
        return texts, metadatas
    except Exception as e:
        print(f"❌ Error extracting data from chunks: {e}")
        return [], []

def init_chromadb(semantic_chunks: List[Any]) -> List[str]:
    """Initialize ChromaDB with semantic chunks (safe initialization)"""
    try:
        collection = get_collection()
        if collection is None:
            return []
        
        texts, metadatas = get_data(semantic_chunks)
        if not texts:
            print("❌ No texts to process")
            return []
            
        embeddings = vector_embeddings(texts)
        if not embeddings:
            print("❌ No embeddings generated")
            return []

        batch_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        print(f"✅ Generated {len(embeddings)} embeddings for batch")
        
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print("✅ Documents added to the collection.")

        # Print current count
        count = collection.count()
        print(f"📊 Collection now contains {count} documents.")

        return batch_ids

    except Exception as e:
        print(f"❌ Error in init_chromadb: {e}")
        return []

# def main():
#     document = TextExtraction.extract_text("../../documents/Referral Bonus Policy.docx")

#     if document is None:
#         raise ValueError("Document extraction failed: No content found.")

#     cleaned_document = TextCleaning.docu_after_cleaning(document)
#     semantic_chunks = TextChuncking.create_chuncks(cleaned_document)

#     print(f"Created {len(semantic_chunks)} semantic chunks.")


#     texts,metadatas=get_data(semantic_chunks)

#     embeddings=vector_embeddings(texts)

#     collection=init_chromadb(texts,metadatas,embeddings)

#     print("done")

# if __name__ == "__main__":
#     main()