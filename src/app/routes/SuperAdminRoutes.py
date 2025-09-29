from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Query, Depends
from uuid import UUID
from typing import Optional, List
from sqlalchemy import func

# Role-based authentication
from src.dependencies.role_auth import require_super_admin, get_admin_id_from_admin
from src.models.admin import Admin, AdminRole
from src.config import Config

from src.service import UploadService
from src.models import UserQuestion, AdminQuestion, TextKnowledge, FileKnowledge, ResponseTime, DeptFailure

     

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
    
    try:
        # Fetch all file records first
        all_files = session.query(FileKnowledge).all()
        total_files = len(all_files)

        if total_files == 0:
            return {
                "message": "No files found to delete",
                "total_files_deleted": 0,
                "vector_db_cleaned": True,
                "deleted_by": str(current_admin.id),
                "admin_name": current_admin.name
            }

        # Delete vectors for each file in vector DB
        vector_results = []
        for file_record in all_files:
            try:
                vec_result = UploadService.delete_vectors_by_knowledge_id(str(file_record.id))
                vector_results.append({
                    "file_id": str(file_record.id),
                    "status": "success" if "error" not in vec_result else "error",
                    "detail": vec_result
                })
            except Exception as ve:
                vector_results.append({
                    "file_id": str(file_record.id),
                    "status": "error",
                    "detail": str(ve)
                })

        # Delete all DB records
        deleted_count = session.query(FileKnowledge).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} files",
            "total_files_deleted": deleted_count,
            "vector_results": vector_results,
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
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

    try:
        # Fetch all text records first
        all_texts = session.query(TextKnowledge).all()
        total_texts = len(all_texts)

        if total_texts == 0:
            return {
                "message": "No text knowledge records found to delete",
                "total_texts_deleted": 0,
                "vector_results": [],
                "deleted_by": str(current_admin.id),
                "admin_name": current_admin.name
            }

        # Delete vectors for each text in vector DB
        vector_results = []
        for text_record in all_texts:
            try:
                vec_result = UploadService.delete_vectors_by_knowledge_id(str(text_record.id))
                vector_results.append({
                    "text_id": str(text_record.id),
                    "status": "success" if "error" not in vec_result else "error",
                    "detail": vec_result
                })
            except Exception as ve:
                vector_results.append({
                    "text_id": str(text_record.id),
                    "status": "error",
                    "detail": str(ve)
                })

        # Delete all DB records
        deleted_count = session.query(TextKnowledge).delete()
        session.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} text knowledge entries",
            "total_texts_deleted": deleted_count,
            "vector_results": vector_results,
            "deleted_by": str(current_admin.id),
            "admin_name": current_admin.name
        }
        
    except HTTPException:
        session.rollback()
        raise
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
    
    try:
        # Get count before deletion
        # total_questions = session.query(UserQuestion).count()
        
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
    
    try:
        # Get count before deletion
        # total_questions = AdminQuestion.get_count()
        
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
    
    try:
        # Get count before deletion
        # total_failures = session.query(DeptFailure).count()
        
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
    
    try:
        # Get count before deletion
        # total_records = session.query(ResponseTime).count()
        
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

@router.put("/admin/resetpassword/{admin_id}")
async def reset_admin_password(
    admin_id: str,
    new_password: str = Body(...),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Reset an admin's password by ID.
    Only super_admin can reset other admins' passwords.
    """

    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    session = Config.get_session()
    try:
        # Validate admin_id format
        try:
            admin_uuid = UUID(admin_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid admin ID format")
        
        # Find admin to reset password
        admin_to_reset = Admin.get_by_id(session, admin_uuid)
        if not admin_to_reset:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Hash new password
        from src.app.routes.AdminAuthRoutes import safe_password_hash
        hashed_password = safe_password_hash(new_password)
        
        # Update password
        admin_to_reset.password = hashed_password
        session.commit()
        
        return {
            "message": f"Password for admin '{admin_to_reset.name}' reset successfully",
            "admin": {
                "id": str(admin_to_reset.id),
                "name": admin_to_reset.name,
                "email": admin_to_reset.email,
                "role": admin_to_reset.role.value
            },
            "reset_by": str(current_admin.id),
            "reset_by_name": current_admin.name
        }
        
    except HTTPException:
        session.rollback()
        raise    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")
    finally:
        session.close()

# purge full vector DB
@router.delete("/vector-db/purge")
async def purge_vector_database(
    confirmation: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_super_admin)
):
    """
    Purge the entire vector database (ChromaDB).
    This will delete ALL collections and vectors permanently.
    Requires super_admin role and confirmation.
    """
    if confirmation != "PURGE_ENTIRE_VECTOR_DB":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Must be 'PURGE_ENTIRE_VECTOR_DB'"
        )
    
    try:
        print(f"🔥 Vector DB purge initiated by admin: {current_admin.name} ({current_admin.email})")
        
        # Import and call the purge function from UploadService
        from src.service.UploadService import purge_all_vectors
        
        # Execute the purge operation
        purge_result = await purge_all_vectors()
        
        if not purge_result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Vector database purge failed: {purge_result.get('message', 'Unknown error')}"
            )
        
        print(f"✅ Vector DB purge completed successfully by {current_admin.name}")
        
        return {
            "message": "Vector database purged successfully",
            "purge_details": {
                "deleted_count": purge_result.get("deleted_count", 0),
                "collections_processed": purge_result.get("collections_processed", 0),
                "successful_deletions": purge_result.get("successful_deletions", 0),
                "deletion_details": purge_result.get("deletion_details", [])
            },
            "operation_message": purge_result.get("message", ""),
            "errors": purge_result.get("errors", []),
            "purged_by": str(current_admin.id),
            "purged_by_name": current_admin.name,
            "purged_by_email": current_admin.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Vector DB purge error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to purge vector database: {str(e)}"
        )
