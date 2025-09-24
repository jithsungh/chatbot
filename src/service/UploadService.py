from ..ingestion import TextChuncking, TextCleaning, TextExtraction, VectorEmbedding



def upload_file(file, dept):
    try:
        # Save the uploaded file to a temporary location
        temp_file_path = f"./documents/temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(file.file.read())

        # Extract text based on file type
        documents = TextExtraction.extract_text(temp_file_path, dept)

        if documents is None:
            return {"error": "Failed to extract text from the document"}

        # Clean the extracted text
        cleaned_documents = TextCleaning.docu_after_cleaning(documents)

        # Chunk the cleaned text
        chunked_documents = TextChuncking.create_chuncks(cleaned_documents)

        # Generate and store vector embeddings
        VectorEmbedding.init_chromadb(chunked_documents)

        return {"message": "File processed and embeddings stored successfully"}
    

    except Exception as e:
        return {"error": str(e)}

def upload_text(text, dept):
    try:
        if not text.strip():
            return {"error": "Input text is empty"}
        
        # Wrap raw text into a LangChain Document with department metadata
        documents = TextExtraction.process_raw_text(text, dept)

        # Clean the input text
        cleaned_text = TextCleaning.docu_after_cleaning(documents)

        # Chunk the cleaned text
        chunked_documents = TextChuncking.create_chuncks(cleaned_text)

        # Generate and store vector embeddings
        VectorEmbedding.init_chromadb(chunked_documents)

        return {"message": "Text processed and embeddings stored successfully"}

    except Exception as e:
        return {"error": str(e)}
    
