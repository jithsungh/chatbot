from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
# import TextCleaning
# import TextExtraction



def init_chuncking():
    # 1. Initialize an embedding model
    # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # embeddings = OpenAIEmbeddings(openai_api_key="")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 2. Initialize the Semantic Chunker
    semantic_chunker = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile", # Other options: "standard_deviation", "interquartile"
    )
    return semantic_chunker


def create_chuncks(cleaned_document):
    semantic_chunker = init_chuncking()
    texts = [doc.page_content for doc in cleaned_document]
    metadatas = [doc.metadata for doc in cleaned_document]
    semantic_chunks = semantic_chunker.create_documents(texts,metadatas)
    return semantic_chunks






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