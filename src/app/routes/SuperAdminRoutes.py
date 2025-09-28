from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Query, Depends
from uuid import UUID
from typing import Optional, List
import asyncio
import os

# Lazy imports - only import when needed
def get_upload_service():
    from src.service import UploadService
    return UploadService

def get_config():
    from src.config import Config
    return Config

def get_question_filter():
    from src.admin.filter import QuestionFilter
    return QuestionFilter

def get_auth_dependencies():
    from src.dependencies.auth import validate_admin_token, get_admin_id_from_token
    return validate_admin_token, get_admin_id_from_token

def get_models():
    from src.models import UserQuestion, AdminQuestion, TextKnowledge
    from src.models.user_question import DeptType
    from src.models.admin_question import AdminQuestionStatus
    return UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus

router = APIRouter()

### need authentication for all routes -> role == super_admin

# delete all files
 
# delete all text knowledge

# delete all user questions

# delete all admin questions

# delete all department failures

# delete all response times

# create admin 

# get all admins

# delete admin by id

# update admin by id

# purge full vector DB
# @router.post("/purge/all")
# async def purge_all_data(
#     secret_password: str = Body(..., embed=True),
#     confirmation: str = Body(..., embed=True),
#     admin_id: str = Depends(get_admin_id_from_token)
# ):
#     """
#     DANGER: Purge ALL data from vector database and PostgreSQL database.
#     This action is IRREVERSIBLE and will delete ALL stored data.
    
#     - secret_password: Must be "bhamakhanda"
#     - confirmation: Must be "DELETE_ALL_DATA_PERMANENTLY"
#     - Requires admin authentication
#     """
#     Config = get_config()
#     UploadService = get_upload_service()
#     UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()
    
#     # Validate secret password
#     if secret_password != Config.SECRET_PASSWORD:
#         raise HTTPException(status_code=403, detail="Invalid secret password")
    
#     # Validate confirmation
#     if confirmation != "DELETE_ALL_DATA_PERMANENTLY":
#         raise HTTPException(status_code=400, detail="Invalid confirmation. Must be 'DELETE_ALL_DATA_PERMANENTLY'")
    
#     session = Config.get_session()
#     purge_results = {
#         "success": False,
#         "vector_db_purged": False,
#         "postgres_purged": False,
#         "errors": [],
#         "purged_by": admin_id,
#         "timestamp": None
#     }
    
#     try:
#         from datetime import datetime
#         purge_results["timestamp"] = datetime.utcnow().isoformat()
        
#         print(f"🚨 DANGER: Starting complete data purge by admin {admin_id}")
        
#         # Step 1: Purge Vector Database
#         try:
#             print("🔥 Purging Vector Database...")
            
#             # Create instance of UploadService and call the method
#             upload_service = UploadService()
#             vector_result = await upload_service.purge_all_vectors()
            
#             if vector_result.get("success", False):
#                 purge_results["vector_db_purged"] = True
#                 purge_results["vector_details"] = vector_result.get("deletion_details", [])
#                 print("✅ Vector database purged successfully")
#             else:
#                 error_msg = f"Vector DB purge failed: {vector_result.get('message', 'Unknown error')}"
#                 purge_results["errors"].append(error_msg)
#                 purge_results["errors"].extend(vector_result.get("errors", []))
#                 print(f"❌ {error_msg}")
                
#         except Exception as e:
#             error_msg = f"Vector database purge exception: {str(e)}"
#             purge_results["errors"].append(error_msg)
#             print(f"❌ {error_msg}")
        
#         # Step 2: Purge PostgreSQL Database
#         try:
#             print("🔥 Purging PostgreSQL Database...")
            
#             # Delete all records from all tables (order matters due to foreign keys)
#             tables_to_purge = [
#                 (UserQuestion, "user_questions"),
#                 (AdminQuestion, "admin_questions"), 
#                 (TextKnowledge, "text_knowledge")
#             ]
            
#             purged_counts = {}
            
#             for model_class, table_name in tables_to_purge:
#                 try:
#                     # Count records before deletion
#                     count_before = session.query(model_class).count()
                    
#                     # Delete all records
#                     deleted_count = session.query(model_class).delete()
                    
#                     purged_counts[table_name] = {
#                         "before": count_before,
#                         "deleted": deleted_count
#                     }
                    
#                     print(f"🗑️  Purged {deleted_count} records from {table_name}")
                    
#                 except Exception as e:
#                     error_msg = f"Failed to purge {table_name}: {str(e)}"
#                     purge_results["errors"].append(error_msg)
#                     print(f"❌ {error_msg}")
            
#             # Commit all database changes
#             session.commit()
#             purge_results["postgres_purged"] = True
#             purge_results["purged_counts"] = purged_counts
            
#             print("✅ PostgreSQL database purged successfully")
            
#         except Exception as e:
#             session.rollback()
#             error_msg = f"PostgreSQL purge exception: {str(e)}"
#             purge_results["errors"].append(error_msg)
#             print(f"❌ {error_msg}")
        
#         # Step 3: Clean up file system (optional)
#         try:
#             import shutil
            
#             # Clean up documents directory if it exists
#             if hasattr(Config, 'DOCUMENTS_PATH') and Config.DOCUMENTS_PATH:
#                 docs_path = Config.DOCUMENTS_PATH
#                 if os.path.exists(docs_path):
#                     deleted_files = []
#                     # Remove all files in documents directory
#                     for filename in os.listdir(docs_path):
#                         file_path = os.path.join(docs_path, filename)
#                         if os.path.isfile(file_path):
#                             try:
#                                 os.remove(file_path)
#                                 deleted_files.append(filename)
#                                 print(f"🗑️  Deleted file: {filename}")
#                             except Exception as file_error:
#                                 error_msg = f"Failed to delete file {filename}: {str(file_error)}"
#                                 purge_results["errors"].append(error_msg)
#                                 print(f"❌ {error_msg}")
                    
#                     purge_results["documents_cleaned"] = True
#                     purge_results["deleted_files"] = deleted_files
                    
#         except Exception as e:
#             error_msg = f"File system cleanup failed: {str(e)}"
#             purge_results["errors"].append(error_msg)
#             print(f"⚠️  {error_msg}")
        
#         # Determine overall success
#         if purge_results["vector_db_purged"] and purge_results["postgres_purged"]:
#             purge_results["success"] = True
#             print("🎉 Complete data purge successful!")
#         else:
#             print("⚠️  Partial purge completed with errors")
        
#         return purge_results
        
#     except Exception as e:
#         session.rollback()
#         error_msg = f"Critical purge failure: {str(e)}"
#         purge_results["errors"].append(error_msg)
#         print(f"💥 {error_msg}")
        
#         raise HTTPException(status_code=500, detail=f"Purge operation failed: {str(e)}")
        
#     finally:
#         session.close()

# @router.post("/purge/vector-only")
# async def purge_vector_db_only(
#     secret_password: str = Body(..., embed=True),
#     admin_id: str = Depends(get_admin_id_from_token)
# ):
#     """
#     Purge ONLY the vector database, keeping PostgreSQL data intact.
#     This will remove all embeddings and vector search capabilities.
    
#     - secret_password: Must be "bhamakhanda"
#     """
#     if secret_password != "bhamakhanda":
#         raise HTTPException(status_code=403, detail="Invalid secret password")
    
#     UploadService = get_upload_service()
    
#     try:
#         from datetime import datetime
        
#         print(f"🔥 Purging Vector Database only by admin {admin_id}")
        
#         # Create instance and purge only vector database
#         upload_service = UploadService()
#         vector_result = await upload_service.purge_all_vectors()
        
#         if vector_result.get("success", False):
#             return {
#                 "success": True,
#                 "message": "Vector database purged successfully",
#                 "postgres_intact": True,
#                 "purged_by": admin_id,
#                 "timestamp": datetime.now().isoformat(),
#                 "vector_details": vector_result.get("deletion_details", []),
#                 "deleted_count": vector_result.get("deleted_count", 0)
#             }
#         else:
#             raise HTTPException(
#                 status_code=500, 
#                 detail=f"Vector database purge failed: {vector_result.get('message', 'Unknown error')}"
#             )
            
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Vector purge failed: {str(e)}")

# @router.get("/purge/status")
# async def get_purge_status(

#     admin_id: str = Depends(get_admin_id_from_token)
# ):
#     """
#     Get current database status - record counts for monitoring purge effects.
#     """
#     Config = get_config()
#     UploadService = get_upload_service()
#     UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()
    
#     session = Config.get_session()
    
#     try:
#         from datetime import datetime
        
#         # Count records in each table
#         user_questions_count = session.query(UserQuestion).count()
#         admin_questions_count = session.query(AdminQuestion).count()
#         text_knowledge_count = session.query(TextKnowledge).count()
        
#         # Get vector database status (if available)
#         vector_status = {"status": "unknown", "count": 0}
#         try:
#             upload_service = UploadService()
#             vector_result = await upload_service.get_vector_count()
#             if vector_result.get("success"):
#                 vector_status = {
#                     "status": "active",
#                     "count": vector_result.get("count", 0),
#                     "collection_details": vector_result.get("collection_details", [])
#                 }
#         except Exception as e:
#             vector_status = {"status": f"error: {str(e)}", "count": 0}
        
#         return {
#             "database_status": {
#                 "user_questions": user_questions_count,
#                 "admin_questions": admin_questions_count,
#                 "text_knowledge": text_knowledge_count,
#                 "total_postgres_records": user_questions_count + admin_questions_count + text_knowledge_count
#             },
#             "vector_database": vector_status,
#             "checked_by": admin_id,
#             "timestamp": datetime.utcnow().isoformat()
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
        
#     finally:
#         session.close()

