from asyncio.log import logger
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Query, Depends, Request
from fastapi.responses import FileResponse
from uuid import UUID
from typing import Optional, List
from sqlalchemy import func
import asyncio
import os
from src.app.routes.AdminAuthRoutes import safe_password_hash, safe_password_verify
from src.service.get_response_times import get_last_n_avg_response_times, INTERVALS_MAP

# Import models and dependencies at the top
from src.models import (
    UserQuestion, AdminQuestion, TextKnowledge, FileKnowledge, 
    ResponseTime, Department, DeptKeyword, Admin, DeptFailure, DeptFailureStatus
)
from src.models.user_question import DeptType
from src.models.dept_failure import DeptCategory
# Role-based authentication
from src.dependencies.role_auth import require_read_only_or_above, get_admin_id_from_admin
from src.config import Config

router = APIRouter()

# Helper function to get admin name by ID
async def get_admin_name(session, admin_id: str) -> Optional[str]:
    """Get admin name from admin_id safely"""
    try:
        admin_uuid = UUID(admin_id)
        return Admin.get_name_by_id(session, admin_uuid)
    except (ValueError, TypeError):
        return None

# Helper function to validate department safely
def validate_department(dept: str) -> DeptType:
    """Validate department string and return DeptType enum"""
    try:
        return DeptType(dept)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid department '{dept}'. Must be one of: {', '.join([d.value for d in DeptType])}"
        )

# Helper function to parse admin ID safely
def parse_admin_id(admin_id_str: str,        current_admin: Admin) -> UUID:
    """Parse admin ID string to UUID safely"""
    if admin_id_str.lower() == "self":
        return current_admin.id
    try:
        return UUID(admin_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid admin ID format")


# get average response times
@router.get("/avg-response-times")
async def get_avg_response_times(
    interval: str = Query(..., description="Interval: 1min, 5min, 1h, etc."),
    n: str = Query("20", description="Number of data points to return"),
    current_admin = Depends(require_read_only_or_above)
):
    session = Config.get_session()
    try:
        # Validate interval
        if interval not in INTERVALS_MAP:
            raise HTTPException(status_code=400, detail=f"Invalid interval: {interval}")

        # Validate n
        try:
            n_int = int(n)
            if n_int <= 0:
                raise ValueError()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid n: {n}. Must be a positive integer.")

        # Fetch data
        data = get_last_n_avg_response_times(session, interval, n_int)
        return {"interval": interval, "n": n_int, "data": data}

    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        # Log the full traceback for debugging
        tb = traceback.format_exc()
        logger.error(f"Error in get_avg_response_times: {str(e)}\n{tb}")
        # Return a generic error message but keep details in server logs
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()


@router.put("/changepassword")
async def change_password(
    current_password: str = Body(..., embed=True, example="oldpassword"),
    new_password: str = Body(..., embed=True, example="newpassword"),
    current_admin: Admin = Depends(require_read_only_or_above),  # ensures logged-in admin
):
    """
    Change password for the current logged-in admin.
    Steps:
      1. Verify current password is correct
      2. Validate new password
      3. Hash new password securely
      4. Update in DB
    """
    if not current_password or not new_password:
        raise HTTPException(
            status_code=400,
            detail="Both 'current_password' and 'new_password' are required",
        )

    if current_password == new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password",
        )

    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 8 characters long",
        )

    session = Config.get_session()
    try:
        # Re-fetch admin record from DB
        admin_record = session.query(Admin).filter(Admin.id == current_admin.id).first()
        if not admin_record:
            raise HTTPException(status_code=404, detail="Admin not found")

        # Verify current password
        if not safe_password_verify(current_password, admin_record.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # Hash new password
        hashed_new_password = safe_password_hash(new_password)

        # Update in DB
        admin_record.password = hashed_new_password
        session.commit()

        return {"message": "Password changed successfully"}

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()



# get all user questions --> modified with better admin filtering
@router.get("/getuserquestions")
async def get_user_questions(
    status: Optional[str] = Query(None),
    dept: Optional[str] = Query(None),
    admin: Optional[str] = Query(None),
    sort_by: bool = Query(False),  # default ascending, true means descending
    limit: int = Query(100, ge=1, le=1000),  # Add pagination
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(require_read_only_or_above)  # Validate admin token
):
    """
    Retrieve user questions based on status, department, and admin.
    - status: Filter by question status (e.g., 'pending', 'processed')
    - dept: Filter by department (e.g., 'HR', 'IT', 'Finance')
    - admin: If 'self', filter only questions tied to the current admin; or specific admin UUID
    - sort_by: If True, sort by createdAt descending (latest first), else ascending
    - limit: Maximum number of results (1-1000)
    - offset: Number of results to skip for pagination
    """
    session = Config.get_session()

    try:
        # Validate status
        valid_statuses = ['pending', 'processed']
        if status and status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Validate department
        if dept:
            validate_department(dept)  # This will raise HTTPException if invalid
        
        query = session.query(UserQuestion)
        
        if status:
            query = query.filter(UserQuestion.status == status)
        if dept:
            dept_enum = DeptType(dept)
            query = query.filter(UserQuestion.dept == dept_enum)

        # Sorting
        if sort_by:
            query = query.order_by(UserQuestion.createdat.desc())
        else:
            query = query.order_by(UserQuestion.createdat.asc())
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        questions = query.offset(offset).limit(limit).all()
        
        # Get admin names for the results
        result = []
        for q in questions:            result.append({
                "id": str(q.id),
                "query": q.query,
                "answer": q.answer,
                "context": q.context,
                "department": q.dept.value if q.dept else None,
                "status": q.status.value if q.status else None,
                "createdAt": q.createdat.isoformat() if q.createdat else None
            })
        
        return {
            "questions": result,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "requested_by": str(current_admin.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

# get all admin questions --> modify
@router.get("/getadminquestions")
async def get_admin_questions(
    status: Optional[str] = Query(None),
    dept: Optional[str] = Query(None),
    admin: Optional[str] = Query(None),
    sort_by: bool = Query(False),  # default ascending, true = descending
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(require_read_only_or_above)  # Validate admin token
):
    """
    Retrieve admin questions based on status, department, and admin.
    - status: Filter by question status (e.g., 'pending', 'processed')
    - dept: Filter by department (e.g., 'HR', 'IT', 'Finance')
    - admin: If 'self', filter only questions tied to the current admin; or specific admin UUID
    - sort_by: If True, sort by createdAt descending (latest first), else ascending
    - limit: Maximum number of results (1-1000)
    - offset: Number of results to skip for pagination
    """
    session = Config.get_session()
    
    try:
        # Validate status
        valid_statuses = ['pending', 'processed']
        if status and status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Validate department
        if dept:
            validate_department(dept)  # This will raise HTTPException if invalid
        
        query = session.query(AdminQuestion)
        
        if status:
            query = query.filter(AdminQuestion.status == status)
        if dept:
            dept_enum = DeptType(dept)
            query = query.filter(AdminQuestion.dept == dept_enum)
        if admin:
            admin_uuid = parse_admin_id(admin, current_admin)
            query = query.filter(AdminQuestion.adminid == admin_uuid)

        # Sorting
        if sort_by:
            query = query.order_by(AdminQuestion.createdat.desc())
        else:
            query = query.order_by(AdminQuestion.createdat.asc())
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        questions = query.offset(offset).limit(limit).all()
        
        # Get admin names for the results
        result = []
        for q in questions:
            admin_name = await get_admin_name(session, str(q.adminid)) if q.adminid else None
            result.append({
                "id": str(q.id),
                "adminid": str(q.adminid) if q.adminid else None,
                "admin_name": admin_name,
                "question": q.question,
                "answer": q.answer if q.answer else None,
                "acceptance": q.notes if q.notes else None,
                "department": q.dept.value if q.dept else None,
                "status": q.status.value if q.status else None,
                "frequency": q.frequency,
                "vectordbid": str(q.vectordbid) if q.vectordbid else None,
                "createdAt": q.createdat.isoformat() if q.createdat else None
            })
        
        return {
            "questions": result,            
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "requested_by": str(current_admin.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

# get all text knowledge --> modify
@router.get("/upload/text")
async def get_all_text_knowledge(
    dept: Optional[str] = Query(None),
    adminid: Optional[str] = Query(None),  # "self" or specific UUID
    sort_by: bool = Query(False),  # default asc, True = desc
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),    current_admin: Admin = Depends(require_read_only_or_above)  # Validate admin token
):
    """
    Retrieve all text knowledge records, optionally filtered by department and admin.
    - dept: Optional department filter (e.g., HR, IT, Finance)
    - adminid: Optional admin ID filter, or 'self' for current admin
    - sort_by: If True, sort by createdAt descending (latest first), else ascending
    - limit: Maximum number of results (1-1000)
    - offset: Number of results to skip for pagination
    """
    session = Config.get_session()
    
    try:
        # Validate department
        if dept:
            validate_department(dept)  # This will raise HTTPException if invalid
        
        # Build query
        query = session.query(TextKnowledge)

        # Department filter
        if dept:
            dept_enum = DeptType(dept)
            query = query.filter(TextKnowledge.dept == dept_enum)

        # Admin filter        if adminid:
            admin_uuid = parse_admin_id(adminid, current_admin)
            query = query.filter(TextKnowledge.adminid == admin_uuid)

        # Sorting
        if sort_by:
            query = query.order_by(TextKnowledge.createdat.desc())
        else:
            query = query.order_by(TextKnowledge.createdat.asc())

        # Total count before pagination
        total_count = query.count()

        # Pagination
        records = query.offset(offset).limit(limit).all()
        
        # Format results with admin names
        result = []
        for record in records:
            admin_name = await get_admin_name(session, str(record.adminid))
            result.append({
                "id": str(record.id),
                "adminid": str(record.adminid),
                "admin_name": admin_name,
                "title": record.title,
                "text": record.text,
                "dept": record.dept.value,
                "createdat": record.createdat.isoformat() if record.createdat else None
            })
        
        return {
            "records": result,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "requested_by": str(current_admin.id)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

# get all uploaded files --> modify
@router.get("/upload/list")
async def list_uploaded_files(
    request: Request,
    dept: Optional[str] = Query(None, description="Optional department filter"),
    admin: Optional[str] = Query(None, description="Filter by admin ('self' or admin_id)"),
    sort_by: Optional[str] = Query("desc", description="Sort by createdat: 'asc' or 'desc'"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),    current_admin: Admin = Depends(require_read_only_or_above)  # Current admin
):
    """
    List uploaded files with optional filters and pagination.
    - dept: Filter by department (HR, IT, Finance, etc.)  
    - admin: 'self' to get only current admin uploads, or admin_id for specific admin  
    - sort_by: 'asc' or 'desc' by created timestamp  
    - limit/offset: Pagination
    """
    session = Config.get_session()
    
    try:
        query = session.query(FileKnowledge)

        # Filter by department
        if dept:
            dept_enum = validate_department(dept)
            query = query.filter(FileKnowledge.dept == dept_enum)

        # Filter by admin        if admin:
            admin_uuid = parse_admin_id(admin, current_admin)
            query = query.filter(FileKnowledge.adminid == admin_uuid)

        # Sort by createdat
        if sort_by and sort_by.lower() == "asc":
            query = query.order_by(FileKnowledge.createdat.asc())
        else:
            query = query.order_by(FileKnowledge.createdat.desc())

        # Total count before pagination
        total_count = query.count()

        # Apply pagination
        records = query.offset(offset).limit(limit).all()

        # Format results with admin names
        result = []
        for r in records:
            admin_name = await get_admin_name(session, str(r.adminid))
            file_url = str(request.url_for("download_file", file_id=str(r.id))) 
            result.append({
                "id": str(r.id),
                "adminid": str(r.adminid),
                "admin_name": admin_name,
                "file_name": r.file_name,
                "file_path": r.file_path,
                "file_url": file_url,
                "dept": r.dept.value,
                "createdat": r.createdat.isoformat() if r.createdat else None
            })

        return {
            "records": result,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "requested_by": str(current_admin.id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list uploaded files: {str(e)}")
    finally:
        session.close()

@router.get("/download/{file_id}", name="download_file")
async def download_file(file_id: str):
    session = Config.get_session()
    
    try:
        record = session.query(FileKnowledge).filter(FileKnowledge.id == file_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = record.file_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(path=file_path, filename=record.file_name)
    
    finally:
        session.close()

# get dept keywords
@router.get("/departments/keywords")
async def get_dept_keywords(
    dept_name: Optional[str] = Query(None, description="Filter by department name (HR, IT, Security)"),
    current_admin: Admin = Depends(require_read_only_or_above)  # Validate admin token
):
    """
    Retrieve department keywords grouped by department name.
    - dept_name: Optional filter by department name (HR, IT, Security)
    Returns: {"HR": [{"id": id, "keyword": "kw1"}, ...], "IT": [...], ...}
    """
    session = Config.get_session()

    try:
        # Build query with join to get department info
        query = session.query(DeptKeyword, Department).join(
            Department, DeptKeyword.dept_id == Department.id
        )
        
        # Filter by department name if provided
        if dept_name:
            dept_enum = validate_department(dept_name)
            query = query.filter(Department.name == dept_enum)
        
        # Execute query
        results = query.all()
        
        # Group keywords by department name
        grouped_keywords = {}
        for keyword, department in results:
            dept_name_key = department.name.value
            if dept_name_key not in grouped_keywords:
                grouped_keywords[dept_name_key] = []
            grouped_keywords[dept_name_key].append({
                "id": str(keyword.id),
                "keyword": keyword.keyword
            })
        
        return grouped_keywords
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

# get descriptions
@router.get("/departments/descriptions")
async def get_dept_descriptions(
    dept_name: Optional[str] = Query(None, description="Filter by department name (HR, IT, Security)"),
    current_admin: Admin = Depends(require_read_only_or_above)  # Validate admin token
):
    """
    Retrieve department descriptions.
    - dept_name: Optional filter by department name (HR, IT, Security)
    """
    session = Config.get_session()
    
    try:
        query = session.query(Department)
        
        # Filter by department name if provided
        if dept_name:
            dept_enum = validate_department(dept_name)
            query = query.filter(Department.name == dept_enum)
        
        departments = query.all()
        
        # Format results
        result = [
            {
                "id": dept.id,
                "name": dept.name.value,
                "description": dept.description,
                "created_at": dept.createdat.isoformat() if dept.createdat else None
            }
            for dept in departments        ]
        
        return {
            "departments": result,
            "total": len(result),
            "requested_by": str(current_admin.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

# get all dept failures
@router.get("/departments/failures")
async def get_dept_failures(
    detected: Optional[str] = Query(None, description="Filter by detected department (HR, IT, Security, General Inquiry)"),
    expected: Optional[str] = Query(None, description="Filter by expected department (HR, IT, Security, General Inquiry)"),
    status: Optional[str] = Query(None, description="Filter by failure status (pending, processed, discarded)"),
    admin: Optional[str] = Query(None, description="Filter by admin ('self' or admin_id)"),
    sort_by: bool = Query(False, description="Sort by created_at: False=ascending, True=descending"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_admin: Admin = Depends(require_read_only_or_above)
):
    """
    Retrieve department failures with optional filters and pagination.
    - detected: Filter by detected department category (HR, IT, Security, General Inquiry)
    - expected: Filter by expected department category (HR, IT, Security, General Inquiry)
    - status: Filter by failure status (pending, processed, discarded)
    - admin: Filter by admin ('self' or specific admin_id)
    - sort_by: If True, sort by created_at descending (latest first), else ascending
    - limit: Maximum number of results (1-1000)
    - offset: Number of results to skip for pagination
    """
    session = Config.get_session()
    
    try:
        # Validate detected department if provided
        valid_dept_categories = ['HR', 'IT', 'Security', 'General Inquiry']
        if detected and detected not in valid_dept_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid detected department '{detected}'. Must be one of: {', '.join(valid_dept_categories)}"
            )
        
        # Validate expected department if provided
        if expected and expected not in valid_dept_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid expected department '{expected}'. Must be one of: {', '.join(valid_dept_categories)}"
            )
        
        # Validate status if provided
        valid_statuses = ['pending', 'processed', 'discarded']
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Build query
        query = session.query(DeptFailure)
        
        # Apply filters
        if detected:
            detected_enum = DeptCategory(detected)
            query = query.filter(DeptFailure.detected == detected_enum)
        
        if expected:
            expected_enum = DeptCategory(expected)
            query = query.filter(DeptFailure.expected == expected_enum)
        
        if status:
            status_enum = DeptFailureStatus(status)
            query = query.filter(DeptFailure.status == status_enum)
        
        if admin:
            admin_uuid = parse_admin_id(admin, current_admin)
            query = query.filter(DeptFailure.adminid == admin_uuid)
        
        # Sorting
        if sort_by:
            query = query.order_by(DeptFailure.created_at.desc())
        else:
            query = query.order_by(DeptFailure.created_at.asc())
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        failures = query.offset(offset).limit(limit).all()
        
        # Format results
        result = []
        for failure in failures:
            admin_name = await get_admin_name(session, str(failure.adminid)) if failure.adminid else None
            result.append({
                "id": str(failure.id),
                "query": failure.query,
                "adminid": str(failure.adminid) if failure.adminid else None,
                "admin_name": admin_name,
                "comments": failure.comments,
                "detected": failure.detected.value if failure.detected else None,
                "expected": failure.expected.value if failure.expected else None,
                "status": failure.status.value if failure.status else None,
                "created_at": failure.created_at.isoformat() if failure.created_at else None
            })
        
        return {
            "failures": result,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "requested_by": str(current_admin.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

# get dashboard stats
@router.get("/dashboard/stats")
async def get_dashboard_stats(current_admin: Admin = Depends(require_read_only_or_above)):
    """
    Retrieve dashboard statistics:
      - number of questions processed
      - number of questions pending
      - average response time (latest)
      - number of files stored
      - number of text knowledge records
      - number of active users
    """
    session = Config.get_session()

    try:
        # Get counts from different tables
        user_questions_count = UserQuestion.get_count(session)
        admin_questions_count = AdminQuestion.get_count(session)
        text_knowledge_count = TextKnowledge.get_count(session)
        file_knowledge_count = FileKnowledge.get_count(session)
        
        # Get pending questions count
        # pending_user_questions = UserQuestion.get_pending_count(session)
        pending_admin_questions = AdminQuestion.get_pending_count(session)

        # Get processed questions count
        # processed_user_questions = UserQuestion.get_processed_count(session)
        processed_admin_questions = AdminQuestion.get_processed_count(session)
        
        # Get latest response time (if available)
        latest_response_time = session.query(ResponseTime).filter(ResponseTime.requests_count > 1).order_by(
            ResponseTime.timestamp.desc()
        ).first()
        
        avg_response_time = latest_response_time.avg_response_time if latest_response_time else 0
        
        # Get active users count (if HistoryManager is available)
        active_users_count = 0
        try:
            if hasattr(Config, 'HISTORY_MANAGER') and Config.HISTORY_MANAGER:
                active_users_count = await Config.HISTORY_MANAGER.get_active_users_count()
        except Exception as e:
            print(f"Warning: Could not get active users count: {e}")
        
        return {
            "total_user_questions": user_questions_count,
            "total_admin_questions": admin_questions_count,
            "total_text_knowledge": text_knowledge_count,
            "total_file_knowledge": file_knowledge_count,
            "pending_questions": pending_admin_questions,
            "processed_questions": processed_admin_questions,            
            "avg_response_time": avg_response_time,
            "active_users": active_users_count,
            "requested_by": str(current_admin.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

@router.get("/router-data-summary")
async def get_router_data_summary(
    current_admin: Admin = Depends(require_read_only_or_above)
):
    """
    Get summary of current router data.
    Requires read-only admin access or above.
    """
    try:
        from src.inference.Pipeline import pipeline
        
        # Initialize pipeline if needed
        pipeline._initialize_components()
        
        # Get data summary
        summary = pipeline.router.get_data_summary()
        
        return {
            "message": "Router data summary retrieved successfully",
            "data_summary": summary,
            "requested_by": str(current_admin.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting router data summary: {str(e)}"
        )

