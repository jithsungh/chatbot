from sentence_transformers import SentenceTransformer
import chromadb
import uuid
# import TextChuncking
# import TextCleaning
# import TextExtraction

MODEL_NAME = "all-MiniLM-L6-v2"


model = SentenceTransformer(MODEL_NAME)



def vector_embeddings(texts):
    embeddings= model.encode(texts)
    if not isinstance(embeddings, list):
        embeddings = embeddings.tolist()
    return embeddings

def get_data(chucks):
    texts = [doc.page_content for doc in chucks]
    metadatas = [doc.metadata for doc in chucks]
    return texts,metadatas

def init_chromadb(semantic_chunks):

    texts,metadatas=get_data(semantic_chunks)
    embeddings=vector_embeddings(texts)

     # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chromadb")
    
    collection = chroma_client.get_or_create_collection(name="TM-DOCS")
    print(f"Chroma Client initialized: {chroma_client}")
    print(f"Collection created or retrieved: {collection.name}")

    batch_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
    print(f"✅ Generated {len(embeddings)} embeddings for batch")
    try:
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print("Documents added to the collection.")

        # print recent documents using batch ids
        recent_docs = collection.get(ids=batch_ids,include=["documents", "metadatas"])
        print(f"Recently added documents: {recent_docs}")


        # print current count of documents in the collection
        count = collection.count()
        print(f"Collection now contains {count} documents.")
        

    except Exception as e:
        print(f"Error while adding documents to the collection: {e}")

    return collection




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