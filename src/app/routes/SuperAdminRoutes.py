from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Query, Depends
from uuid import UUID
from typing import Optional, List
from sqlalchemy import func

# Role-based authentication
from src.dependencies.role_auth import require_super_admin, get_admin_id_from_admin
from src.models.admin import Admin, AdminRole
from src.config import Config

# Lazy imports - only import when needed
def get_upload_service():
    from src.service import UploadService
    return UploadService

def get_models():
    from src.models import (
        UserQuestion, AdminQuestion, TextKnowledge, FileKnowledge, 
        ResponseTime, DeptFailure
    )
    from src.models.user_question import DeptType
    from src.models.admin_question import AdminQuestionStatus
    return UserQuestion, AdminQuestion, TextKnowledge, FileKnowledge, ResponseTime, DeptFailure, DeptType, AdminQuestionStatus

router = APIRouter()

### All routes require super_admin role authentication

# Delete all files
@router.delete("/files/all")
async def delete_all_files(
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Delete all uploaded files from database and vector store.
    Requires super_admin role and confirmation.
    """
    if confirmation != "DELETE_ALL_FILES":
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation. Must be 'DELETE_ALL_FILES'"
        )
    
    session = Config.get_session()
    UploadService = get_upload_service()
    FileKnowledge, *_ = get_models()
    
    try:
        # Get count before deletion
        total_files = session.query(FileKnowledge).count()
        
        # Delete from vector database
        upload_service = UploadService()
        vector_result = await upload_service.purge_all_file_vectors()
        
        # Delete from database
        deleted_count = session.query(FileKnowledge).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} files",
            "total_files_deleted": deleted_count,
            "vector_db_cleaned": vector_result.get("success", False),
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete files: {str(e)}")
    finally:
        session.close()

# Delete all text knowledge
@router.delete("/text/all")
async def delete_all_text_knowledge(
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Delete all text knowledge from database and vector store.
    Requires super_admin role and confirmation.
    """
    if confirmation != "DELETE_ALL_TEXT":
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation. Must be 'DELETE_ALL_TEXT'"
        )
    
    session = Config.get_session()
    UploadService = get_upload_service()
    _, _, TextKnowledge, *_ = get_models()
    
    try:
        # Get count before deletion
        total_texts = session.query(TextKnowledge).count()
        
        # Delete from vector database
        upload_service = UploadService()
        vector_result = await upload_service.purge_all_text_vectors()
        
        # Delete from database
        deleted_count = session.query(TextKnowledge).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} text knowledge entries",
            "total_texts_deleted": deleted_count,
            "vector_db_cleaned": vector_result.get("success", False),
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete text knowledge: {str(e)}")
    finally:
        session.close()

# Delete all user questions
@router.delete("/user-questions/all")
async def delete_all_user_questions(
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Delete all user questions from database.
    Requires super_admin role and confirmation.
    """
    if confirmation != "DELETE_ALL_USER_QUESTIONS":
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation. Must be 'DELETE_ALL_USER_QUESTIONS'"
        )
    
    session = Config.get_session()
    UserQuestion, *_ = get_models()
    
    try:
        # Get count before deletion
        total_questions = session.query(UserQuestion).count()
        
        # Delete all user questions
        deleted_count = session.query(UserQuestion).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} user questions",
            "total_questions_deleted": deleted_count,
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user questions: {str(e)}")
    finally:
        session.close()

# Delete all admin questions
@router.delete("/admin-questions/all")
async def delete_all_admin_questions(
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Delete all admin questions from database.
    Requires super_admin role and confirmation.
    """
    if confirmation != "DELETE_ALL_ADMIN_QUESTIONS":
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation. Must be 'DELETE_ALL_ADMIN_QUESTIONS'"
        )
    
    session = Config.get_session()
    _, AdminQuestion, *_ = get_models()
    
    try:
        # Get count before deletion
        total_questions = session.query(AdminQuestion).count()
        
        # Delete all admin questions
        deleted_count = session.query(AdminQuestion).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} admin questions",
            "total_questions_deleted": deleted_count,
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete admin questions: {str(e)}")
    finally:
        session.close()

# Delete all department failures
@router.delete("/dept-failures/all")
async def delete_all_dept_failures(
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Delete all department failures from database.
    Requires super_admin role and confirmation.
    """
    if confirmation != "DELETE_ALL_DEPT_FAILURES":
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation. Must be 'DELETE_ALL_DEPT_FAILURES'"
        )
    
    session = Config.get_session()
    *_, DeptFailure, _, _ = get_models()
    
    try:
        # Get count before deletion
        total_failures = session.query(DeptFailure).count()
        
        # Delete all department failures
        deleted_count = session.query(DeptFailure).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} department failures",
            "total_failures_deleted": deleted_count,
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete department failures: {str(e)}")
    finally:
        session.close()

# Delete all response times
@router.delete("/response-times/all")
async def delete_all_response_times(
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Delete all response time records from database.
    Requires super_admin role and confirmation.
    """
    if confirmation != "DELETE_ALL_RESPONSE_TIMES":
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation. Must be 'DELETE_ALL_RESPONSE_TIMES'"
        )
    
    session = Config.get_session()
    *_, ResponseTime, _, _ = get_models()
    
    try:
        # Get count before deletion
        total_records = session.query(ResponseTime).count()
        
        # Delete all response time records
        deleted_count = session.query(ResponseTime).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} response time records",
            "total_records_deleted": deleted_count,
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete response times: {str(e)}")
    finally:
        session.close()

# Create admin
@router.post("/admin/create")
async def create_admin(
    name: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    role: str = Body(...),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Create a new admin with specified role.
    Only super_admin can create other admins.
    """
    # Validate role
    try:
        admin_role = AdminRole(role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{role}'. Must be one of: {', '.join([r.value for r in AdminRole])}"
        )
    
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    session = Config.get_session()
    try:
        # Check if email already exists
        existing_admin = Admin.get_by_email(session, email)
        if existing_admin:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        from src.app.routes.AdminAuthRoutes import safe_password_hash
        hashed_password = safe_password_hash(password)
        
        # Create new admin
        new_admin = Admin.create(
            session=session,
            name=name,
            email=email,
            password=hashed_password,
            enabled=True,
            verification_token=None
        )
        
        # Set role
        new_admin.role = admin_role
        session.commit()
        
        return {
            "message": "Admin created successfully",
            "admin": {
                "id": str(new_admin.id),
                "name": new_admin.name,
                "email": new_admin.email,
                "role": new_admin.role.value,
                "enabled": new_admin.enabled
            },
            "created_by": str(current_admin.id),
            "created_by_name": current_admin.name
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")
    finally:
        session.close()

# Get all admins
@router.get("/admins")
async def get_all_admins(
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Get all admin accounts with their details.
    Only super_admin can view all admins.
    """
    session = Config.get_session()
    try:
        admins = Admin.get_all(session)
        return {
            "admins": [
                {
                    "id": str(admin.id),
                    "name": admin.name,
                    "email": admin.email,
                    "role": admin.role.value,
                    "enabled": admin.enabled,
                    "verified": admin.verified,
                    "last_login": admin.last_login.isoformat() if admin.last_login else None,
                    "created_at": admin.created_at.isoformat() if admin.created_at else None
                }
                for admin in admins
            ],
            "total_count": len(admins),
            "requested_by": str(current_admin.id)
        }
    finally:
        session.close()

# Delete admin by id
@router.delete("/admin/{admin_id}")
async def delete_admin(
    admin_id: str,
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Delete an admin account by ID.
    Super admin cannot delete themselves.
    """
    if confirmation != "DELETE_ADMIN":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Must be 'DELETE_ADMIN'"
        )
    
    # Prevent self-deletion
    if admin_id == str(current_admin.id):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own admin account"
        )
    
    session = Config.get_session()
    try:
        # Validate admin_id format
        try:
            admin_uuid = UUID(admin_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid admin ID format")
        
        # Find admin to delete
        admin_to_delete = Admin.get_by_id(session, admin_uuid)
        if not admin_to_delete:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Delete the admin
        deleted = Admin.delete_by_id(session, admin_uuid)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete admin")
        
        return {
            "message": f"Admin '{admin_to_delete.name}' deleted successfully",
            "deleted_admin": {
                "id": admin_id,
                "name": admin_to_delete.name,
                "email": admin_to_delete.email,
                "role": admin_to_delete.role.value
            },
            "deleted_by": str(current_admin.id),
            "deleted_by_name": current_admin.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete admin: {str(e)}")
    finally:
        session.close()

# Update admin by id
@router.put("/admin/{admin_id}")
async def update_admin(
    admin_id: str,
    name: Optional[str] = Body(None),
    email: Optional[str] = Body(None),
    role: Optional[str] = Body(None),
    enabled: Optional[bool] = Body(None),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Update an admin account by ID.
    Super admin can update any admin except cannot disable themselves.
    """
    session = Config.get_session()
    try:
        # Validate admin_id format
        try:
            admin_uuid = UUID(admin_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid admin ID format")
        
        # Find admin to update
        admin_to_update = Admin.get_by_id(session, admin_uuid)
        if not admin_to_update:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Prevent self-disabling
        if admin_id == str(current_admin.id) and enabled is False:
            raise HTTPException(
                status_code=400,
                detail="Cannot disable your own admin account"
            )
        
        # Update fields
        updated_fields = []
        
        if name is not None:
            admin_to_update.name = name
            updated_fields.append("name")
        
        if email is not None:
            # Check if email already exists for another admin
            existing_admin = Admin.get_by_email(session, email)
            if existing_admin and existing_admin.id != admin_uuid:
                raise HTTPException(status_code=400, detail="Email already in use by another admin")
            admin_to_update.email = email
            updated_fields.append("email")
        
        if role is not None:
            try:
                admin_role = AdminRole(role)
                admin_to_update.role = admin_role
                updated_fields.append("role")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role '{role}'. Must be one of: {', '.join([r.value for r in AdminRole])}"
                )
        
        if enabled is not None:
            admin_to_update.enabled = enabled
            updated_fields.append("enabled")
        
        if not updated_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        session.commit()
        
        return {
            "message": f"Admin '{admin_to_update.name}' updated successfully",
            "updated_fields": updated_fields,
            "admin": {
                "id": str(admin_to_update.id),
                "name": admin_to_update.name,
                "email": admin_to_update.email,
                "role": admin_to_update.role.value,
                "enabled": admin_to_update.enabled
            },
            "updated_by": str(current_admin.id),
            "updated_by_name": current_admin.name
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update admin: {str(e)}")
    finally:
        session.close()

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

