from ..ingestion import TextChuncking, TextCleaning, TextExtraction, VectorEmbedding
from src.config import Config
import os

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
def get_client():
    """Get the shared ChromaDB client (lazy loaded)"""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
        return client
    except Exception as e:
        print(f"❌ Error creating ChromaDB client: {e}")
        return None

global chroma_collection
global client
chroma_collection = get_collection()
client = get_client()


async def upload_file(file, dept, file_uuid):
    try:
        # Sanitize filename -> replace spaces with underscores
        safe_filename = os.path.basename(file.filename).replace(" ", "_")

        # Save the uploaded file to a temporary location
        file_path = f"{Config.DOCUMENTS_PATH}/{file_uuid}_{safe_filename}"
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Extract text based on file type
        documents = TextExtraction.extract_text(file_path, dept, file_uuid)

        if documents is None:
            return {"error": "Failed to extract text from the document"}

        # Clean the extracted text
        cleaned_documents = TextCleaning.docu_after_cleaning(documents)

        # Chunk the cleaned text
        chunked_documents = TextChuncking.create_chuncks(cleaned_documents)

        # Generate and store vector embeddings
        VectorEmbedding.init_chromadb(chunked_documents)

        return file_path
    
    except Exception as e:
        return {"error": str(e)}
    

def delete_vectors_by_knowledge_id(knowledge_id: str):
    global chroma_collection   # ✅ tell Python to use the global variable
    
    if chroma_collection is None:
        chroma_collection = get_collection()

    if not chroma_collection:
        return {"error": "Vector database chroma_collection not initialized"}

    try:
        results = chroma_collection.query(where={"knowledge_id": knowledge_id}, include=["ids"])
        
        vector_ids = results.get("ids", [])
        if not vector_ids:
            return {"message": f"No vectors found for knowledge_id: {knowledge_id}"}
        
        chroma_collection.delete(ids=vector_ids)
        return {"message": f"Deleted {len(vector_ids)} vectors for knowledge_id: {knowledge_id}"}
    
    except Exception as e:
        return {"error": str(e)}

      

async def upload_answer(question, answer, dept, pid=None):
    try:
        if not question.strip() or not answer.strip():
            return {"error": "Question or answer is empty"}
        
        # Ensure dept is a string
        if hasattr(dept, 'value'):
            dept = dept.value
        
        # Wrap Q&A into a LangChain Document with department metadata
        document = TextExtraction.process_qa_text(f"Q: {question}\nA: {answer}", dept, pid)
        
        if document is None:
            return {"error": "Failed to create document from Q&A"}

        # Store in vector database and get document IDs
        document_ids = VectorEmbedding.init_chromadb([document])
        
        if document_ids and len(document_ids) > 0:
            return {
                "message": "Q&A processed and embeddings stored successfully",
                "document_id": document_ids[0]
            }
        else:
            return {"error": "Failed to get document ID from vector database"}
        
    except Exception as e:
        return {"error": str(e)}

async def upload_text(text, dept, title, text_uuid=None):
    try:
        if not text.strip():
            return {"error": "Input text is empty"}
        
        # Wrap raw text into a LangChain Document with department metadata
        documents = TextExtraction.process_raw_text(text, dept, title, text_uuid)

        # Clean the input text
        cleaned_text = TextCleaning.docu_after_cleaning(documents)

        # Chunk the cleaned text
        chunked_documents = TextChuncking.create_chuncks(cleaned_text)

        # Generate and store vector embeddings
        VectorEmbedding.init_chromadb(chunked_documents)

        return {"message": "Text processed and embeddings stored successfully"}

    except Exception as e:
        return {"error": str(e)}
    

async def purge_all_vectors():
    """
    Purge all vectors from the vector database.
    Returns a dictionary with operation results.
    """
    try:
        print("🔥 Starting vector database purge operation...")
        
        # Initialize result object
        result = {
            "success": False,
            "message": "",
            "deleted_count": 0,
            "errors": []
        }

        
        try:
            global client
            if client is None:
                client = get_client()            # Get all collections to purge
            collections = []
            try:
                # List all collections in ChromaDB
                collections_list = client.list_collections()
                collections = [collection.name for collection in collections_list]
                print(f"Found {len(collections)} collections to purge: {collections}")
            except Exception as list_error:
                print(f"⚠️ Could not list collections: {list_error}")
                # Use default collection name as fallback
                collections = [Config.COLLECTION_NAME]

            if not collections:
                print("No collections found to purge")
                result["success"] = True
                result["message"] = "No collections found - vector database is already empty"
                return result

            total_deleted = 0
            deletion_results = []

            # Purge each collection
            for collection_name in collections:
                try:
                    print(f"🗑️ Purging collection: {collection_name}")
                    
                    # Get the collection
                    collection = client.get_collection(name=collection_name)
                    
                    # Get count before deletion
                    try:
                        collection_count = collection.count()
                        print(f"Collection {collection_name} has {collection_count} documents")
                    except:
                        collection_count = 0

                    # Delete the entire collection
                    client.delete_collection(name=collection_name)
                    print(f"✅ Deleted collection: {collection_name} ({collection_count} documents)")
                    
                    deletion_results.append({
                        "collection": collection_name,
                        "deleted": collection_count,
                        "status": "success"
                    })
                    
                    total_deleted += collection_count

                except Exception as collection_error:
                    error_msg = f"Failed to purge collection {collection_name}: {str(collection_error)}"
                    print(f"❌ {error_msg}")
                    
                    deletion_results.append({
                        "collection": collection_name,
                        "deleted": 0,
                        "status": "error",
                        "error": str(collection_error)
                    })
                    
                    result["errors"].append(error_msg)

            # Additional cleanup - reset ChromaDB if possible
            try:
                # Reset the ChromaDB instance (if method exists)
                if hasattr(client, 'reset'):
                    client.reset()
                    print("✅ ChromaDB reset completed")
            except Exception as reset_error:
                print(f"⚠️ Reset operation failed: {reset_error}")
                # Don't add reset errors to the main errors array as they are not critical
                result["reset_warning"] = f"Reset failed: {str(reset_error)}"

            # Determine success status
            successful_deletions = len([r for r in deletion_results if r["status"] == "success"])
            has_critical_errors = len(result["errors"]) > 0
            
            # Success if we successfully deleted at least one collection and no critical errors occurred
            result["success"] = successful_deletions > 0
            result["deleted_count"] = total_deleted
            result["collections_processed"] = len(deletion_results)
            result["successful_deletions"] = successful_deletions
            result["deletion_details"] = deletion_results

            if result["success"]:
                if has_critical_errors:
                    result["message"] = f"Partial purge completed: {successful_deletions}/{len(collections)} collections purged with {total_deleted} total vectors deleted, but some errors occurred"
                    print(f"⚠️ {result['message']}")
                else:
                    result["message"] = f"Successfully purged {successful_deletions} collections with {total_deleted} total vectors deleted"
                    print(f"🎉 {result['message']}")
            else:
                result["message"] = "Vector database purge failed - no collections were successfully purged"
                print(f"💥 {result['message']}")

        except Exception as db_error:
            error_msg = f"Database connection error: {str(db_error)}"
            print(f"❌ {error_msg}")
            result["errors"].append(error_msg)
            result["message"] = f"Failed to connect to vector database: {str(db_error)}"

        return result

    except Exception as error:
        print(f"💥 Critical error during vector database purge: {error}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": f"Vector database purge failed: {str(error)}",
            "deleted_count": 0,
            "errors": [str(error)],
            "timestamp": None
        }

async def get_vector_count():
    """
    Get the total count of vectors in the vector database.
    Returns a dictionary with count information.
    """
    try:
        global client        
        if client is None:
            client = get_client()

        total_count = 0
        collection_counts = []

        try:
            # Get all collections
            collections_list = client.list_collections()
            collections = [collection.name for collection in collections_list]
        except Exception as list_error:
            print(f"Could not list collections: {list_error}")
            # Use default collection name as fallback
            collections = [Config.COLLECTION_NAME]
        
        for collection_name in collections:
            try:
                # Get the collection
                collection = client.get_collection(name=collection_name)
                
                # Get count from collection
                count = collection.count()
                
                collection_counts.append({
                    "collection": collection_name,
                    "count": count
                })
                
                total_count += count
                
            except Exception as coll_error:
                print(f"Could not get count for collection {collection_name}: {coll_error}")
                collection_counts.append({
                    "collection": collection_name,
                    "count": 0,
                    "error": str(coll_error)
                })

        return {
            "success": True,
            "count": total_count,
            "collection_details": collection_counts
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
            "count": 0
        }
