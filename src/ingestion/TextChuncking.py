from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import Config
import threading

# Cache the semantic chunker to avoid re-initialization
_semantic_chunker = None
_chunker_lock = threading.Lock()

def init_chuncking():
    """Initialize and cache the semantic chunker"""
    global _semantic_chunker
    
    if _semantic_chunker is None:
        with _chunker_lock:
            if _semantic_chunker is None:
                print(f"🔄 Initializing SemanticChunker with model: {Config.DEFAULT_MODEL_NAME}")
                
                # Use the same model name as your shared model
                model_name = Config.DEFAULT_MODEL_NAME
                embeddings = HuggingFaceEmbeddings(model_name=f"sentence-transformers/{model_name}")

                # Initialize the Semantic Chunker (cached)
                _semantic_chunker = SemanticChunker(
                    embeddings=embeddings,
                    breakpoint_threshold_type="percentile", # Other options: "standard_deviation", "interquartile"
                )
                print(f"✅ SemanticChunker initialized and cached")
    
    return _semantic_chunker

def create_chuncks(cleaned_document):
    """Create semantic chunks using cached chunker"""
    semantic_chunker = init_chuncking()  # Returns cached instance
    
    # Extract texts and metadata from cleaned document
    if hasattr(cleaned_document[0], 'page_content'):
        # If cleaned_document is already a list of Document objects
        texts = [doc.page_content for doc in cleaned_document]
        metadatas = [doc.metadata for doc in cleaned_document]
    else:
        # If cleaned_document is raw text or list of strings
        if isinstance(cleaned_document, str):
            texts = [cleaned_document]
            metadatas = [{"source": "document"}]
        else:
            texts = cleaned_document
            metadatas = [{"source": f"chunk_{i}"} for i in range(len(texts))]
    
    # Create semantic chunks
    semantic_chunks = semantic_chunker.create_documents(texts, metadatas)
    return semantic_chunks

def clear_chunker_cache():
    """Clear the cached chunker (useful for testing or memory management)"""
    global _semantic_chunker
    with _chunker_lock:
        _semantic_chunker = None
        print("🗑️ SemanticChunker cache cleared")




# def main():


#     document = TextExtraction.extract_text("../../documents/Referral Bonus Policy.docx")

#     if document is None:
#         raise ValueError("Document extraction failed: No content found.")


#     cleaned_document = TextCleaning.docu_after_cleaning(document)

#     semantic_chunks = create_chuncks(cleaned_document)

#     print(f"Created {len(semantic_chunks)} semantic chunks.")

#     for chunk in semantic_chunks:
#         print("Chunk content:", chunk.page_content)
#         print("Chunk metadata:", chunk.metadata)
#         print("--------------------------------------------")


# if __name__ == "__main__":
#     main()