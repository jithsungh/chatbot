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

# Get auth dependencies once
validate_admin_token, get_admin_id_from_token = get_auth_dependencies()

@router.post("/upload/file/{dept}")
async def upload_file(
    dept: str,
    file: UploadFile = File(...),
    admin_id: str = Depends(get_admin_id_from_token)
):
    """Upload a single file to be processed and stored in the vector database."""
    Config = get_config()
    UploadService = get_upload_service()
    
    # Validate department
    if not dept or not dept.strip():
        raise HTTPException(status_code=400, detail="Department is required")
    if dept not in Config.DEPARTMENTS:
        raise HTTPException(status_code=400, detail="Invalid department specified")
    
    # Validate file
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")
    
    # Check file size
    max_file_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_file_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB")
    
    try:
        result = await UploadService.upload_file(file, dept)
        return {
            "result": result,
            "uploaded_by": admin_id,
            "department": dept,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.post("/upload/files/{dept}")
async def upload_multiple_files(
    dept: str,
    files: List[UploadFile] = File(...),
    admin_id: str = Depends(get_admin_id_from_token)
):
    """Upload multiple files to be processed individually and stored in the vector database."""
    Config = get_config()
    UploadService = get_upload_service()
    
    # Validate department
    if not dept or not dept.strip():
        raise HTTPException(status_code=400, detail="Department is required")
    if dept not in Config.DEPARTMENTS:
        raise HTTPException(status_code=400, detail="Invalid department specified")
    
    # Validate files
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Check number of files limit
    max_files = 10  # Limit to prevent server overload
    if len(files) > max_files:
        raise HTTPException(status_code=400, detail=f"Too many files. Maximum is {max_files} files")
    
    # Validate each file before processing
    max_file_size = 10 * 1024 * 1024  # 10MB
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail=f"File must have a filename")
        
        # Read file content to get actual size if file.size is None
        if file.size is None:
            content = await file.read()
            actual_size = len(content)
            # Reset file pointer
            await file.seek(0)
        else:
            actual_size = file.size
            
        if actual_size > max_file_size:
            raise HTTPException(status_code=413, detail=f"File '{file.filename}' too large. Maximum size is 10MB")   
    
    # Process files individually
    results = []
    successful_uploads = 0
    failed_uploads = 0
    
    for i, file in enumerate(files):
        try:
            print(f"📄 Processing file {i+1}/{len(files)}: {file.filename}")
            
            # Process each file individually
            result = await UploadService.upload_file(file, dept)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "result": result,
                "file_index": i + 1
            })
            successful_uploads += 1
            
            print(f"✅ Successfully processed: {file.filename}")
            
            # Add small delay between files to prevent overwhelming the system
            await asyncio.sleep(0.1)
            
        except Exception as e:
            error_msg = f"Failed to process '{file.filename}': {str(e)}"
            print(f"❌ {error_msg}")
            
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e),
                "file_index": i + 1
            })
            failed_uploads += 1
            
            # Continue processing other files even if one fails
            continue
    
    # Summary response
    return {
        "message": f"Processed {len(files)} files",
        "successful_uploads": successful_uploads,
        "failed_uploads": failed_uploads,
        "total_files": len(files),
        "department": dept,
        "uploaded_by": admin_id,
        "results": results
    }

async def process_single_file(file: UploadFile, dept: str, file_index: int):
    """Helper function to process a single file asynchronously"""
    UploadService = get_upload_service()
    
    try:
        print(f"🔄 Processing file {file_index}: {file.filename}")
        result = await UploadService.upload_file(file, dept)
        print(f"✅ Completed file {file_index}: {file.filename}")
        
        return {
            "filename": file.filename,
            "status": "success",
            "result": result,
            "file_index": file_index
        }
    except Exception as e:
        print(f"❌ Failed file {file_index}: {file.filename} - {str(e)}")
        return {
            "filename": file.filename,
            "status": "error",
            "error": str(e),
            "file_index": file_index
        }

@router.post("/upload/files/batch/{dept}")
async def upload_files_batch(
    dept: str,
    files: List[UploadFile] = File(...),
    concurrent_limit: int = Query(3, ge=1, le=5, description="Number of files to process concurrently"),
    admin_id: str = Depends(get_admin_id_from_token)
):
    """
    Upload multiple files with controlled concurrency for better performance.
    Files are processed in batches to prevent server overload.
    """
    Config = get_config()
    
    # Validate department
    if not dept or not dept.strip():
        raise HTTPException(status_code=400, detail="Department is required")
    if dept not in Config.DEPARTMENTS:
        raise HTTPException(status_code=400, detail="Invalid department specified")
    
    # Validate files
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Check limits
    max_files = 50
    if len(files) > max_files:
        raise HTTPException(status_code=400, detail=f"Too many files. Maximum is {max_files} files")
    
    max_file_size = 10 * 1024 * 1024  # 10MB
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="All files must have filenames")
        if file.size and file.size > max_file_size:
            raise HTTPException(status_code=413, detail=f"File '{file.filename}' too large. Maximum size is 10MB")
    
    # Process files in batches with controlled concurrency
    results = []
    successful_uploads = 0
    failed_uploads = 0
    
    # Create batches
    for i in range(0, len(files), concurrent_limit):
        batch = files[i:i + concurrent_limit]
        batch_tasks = []
        
        # Create tasks for current batch
        for j, file in enumerate(batch):
            file_index = i + j + 1
            task = process_single_file(file, dept, file_index)
            batch_tasks.append(task)
        
        # Process current batch concurrently
        print(f"🚀 Processing batch {i//concurrent_limit + 1} with {len(batch)} files")
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Process batch results
        for result in batch_results:
            if isinstance(result, Exception):
                failed_uploads += 1
                results.append({
                    "filename": "unknown",
                    "status": "error",
                    "error": str(result),
                    "file_index": len(results) + 1
                })
            else:
                if result["status"] == "success":
                    successful_uploads += 1
                else:
                    failed_uploads += 1
                results.append(result)
        
        # Small delay between batches
        if i + concurrent_limit < len(files):
            await asyncio.sleep(0.5)
    
    return {
        "message": f"Batch processing completed for {len(files)} files",
        "successful_uploads": successful_uploads,
        "failed_uploads": failed_uploads,
        "total_files": len(files),
        "concurrent_limit": concurrent_limit,
        "department": dept,
        "uploaded_by": admin_id,
        "results": results
    }

@router.post("/upload/text/{dept}")
async def upload_text(
    dept: str,
    title: str = Body(..., embed=True),
    text: str = Body(..., embed=True),
    admin_id: str = Depends(get_admin_id_from_token)
):
    """Upload raw text to be processed and stored in the vector database."""
    Config = get_config()
    UploadService = get_upload_service()
    UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()
    
    session = Config.get_session()
    
    try:
        # Validate inputs
        if not dept or not dept.strip():
            raise HTTPException(status_code=400, detail="Department is required")
        if dept not in Config.DEPARTMENTS:
            raise HTTPException(status_code=400, detail="Invalid department specified")
        
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text content cannot be empty")
        
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        # Validate text length
        if len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text content must be at least 10 characters")
        
        if len(title.strip()) > 255:
            raise HTTPException(status_code=400, detail="Title must be less than 255 characters")
        
        # Convert admin_id from token to UUID
        try:
            admin_uuid = UUID(admin_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid admin ID from token")
        
        # Convert department string to enum
        try:
            dept_enum = DeptType(dept)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid department specified")
        
        # Store in the postgres database
        text_knowledge = TextKnowledge.create(
            session=session,
            adminid=admin_uuid,
            title=title,
            text=text,
            dept=dept_enum
        )
        
        # Process through upload service for vector database storage - ADD AWAIT HERE
        result = await UploadService.upload_text(text, dept, title)
        
        # Check if vector processing was successful
        if "error" in result:
            return {
                "success": True,
                "message": "Text stored in database but vector processing failed",
                "database_id": str(text_knowledge.id),
                "vector_error": result["error"],
                "uploaded_by": admin_id
            }
        
        return {
            "success": True,
            "message": "Text successfully stored in database and vector database",
            "database_id": str(text_knowledge.id),
            "result": result,
            "uploaded_by": admin_id
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

@router.get("/upload/text")
async def get_all_text_knowledge(
    dept: str | None = Query(None),
    adminid: str | None = Query(None),
    token_payload: dict = Depends(validate_admin_token)  # Validate admin token
):
    """
    Retrieve all text knowledge records, optionally filtered by department and admin.
    - dept: Optional department filter (e.g., HR, IT, Finance)
    - adminid: Optional admin ID filter
    """
    Config = get_config()  # Add this line
    UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()  # Add this line
    
    session = Config.get_session()
    try:
        # Initialize admin_uuid to None
        admin_uuid = None
        
        # Validate department
        if dept and dept not in Config.DEPARTMENTS:
            raise HTTPException(status_code=400, detail="Invalid department specified")
        
        # Validate and convert adminid
        if adminid:
            try:
                admin_uuid = UUID(adminid)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid adminid format")
            
        # Build query
        query = session.query(TextKnowledge)

        # Apply filters
        if dept:
            try:
                dept_enum = DeptType(dept)
                query = query.filter(TextKnowledge.dept == dept_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid department specified")
                
        if admin_uuid:
            query = query.filter(TextKnowledge.adminid == admin_uuid)

        # Execute query
        records = query.all()
        
        # Format results
        result = [
            {
                "id": str(record.id),
                "adminid": str(record.adminid),
                "title": record.title,
                "text": record.text,
                "dept": record.dept.value,
                "createdat": record.createdat.isoformat() if record.createdat else None
            }
            for record in records
        ]
        
        return {
            "records": result,
            "total": len(result),
            "requested_by": token_payload["admin_id"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()


@router.get("/upload/list")
async def list_uploaded_files(
    admin_id: str = Depends(get_admin_id_from_token)  # Validate admin token
):
    """
    List all uploaded files in the system.
    """
    Config = get_config()  # Add this line 

    upload_dir = Config.DOCUMENTS_PATH
    
    # Validate upload directory exists
    if not os.path.exists(upload_dir):
        raise HTTPException(status_code=404, detail="Upload directory not found")
    
    try:
        files = os.listdir(upload_dir)
        # Filter only files (not directories)
        files = [f for f in files if os.path.isfile(os.path.join(upload_dir, f))]
        
        return {
            "files": files,
            "total_files": len(files),
            "requested_by": admin_id
        }
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied to access upload directory")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.post("/summarize")
async def summarize_pending_questions(
    admin_id: str = Depends(get_admin_id_from_token)  # Validate admin token
):
    """
    Summarize pending admin questions using the QuestionFilter service.
    """
    Config = get_config()  # Add this line
    QuestionFilter = get_question_filter()  # Add this line
    session = Config.get_session()
    try:
        # Initialize filter instance
        question_filter = QuestionFilter()
        
        result = question_filter.filter_and_process_questions(
            session=session,
            similarity_threshold=0.4,
            default_admin_id=None
        )
        
        print("\n" + "="*50)
        print("PIPELINE TEST RESULTS")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Questions Added: {result['questions_added']}")
        if result.get('questions_processed'):
            print(f"Questions Processed: {result['questions_processed']}")
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        print("="*50)
        
        # Add admin info to result
        result["processed_by"] = admin_id
        
        return result
        
    except Exception as e:
        print(f"❌ Test pipeline failed: {e}")
        return {
            "success": False, 
            "errors": [str(e)],
            "processed_by": admin_id
        }
    finally:
        session.close()

@router.get("/getuserquestions")
async def get_user_questions(
    status: str | None = Query(None),
    dept: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),  # Add pagination
    offset: int = Query(0, ge=0),
    admin_id: str = Depends(get_admin_id_from_token)  # Validate admin token
):
    """
    Retrieve user questions based on status and department.
    - status: Filter by question status (e.g., 'pending', 'processed')
    - dept: Filter by department (e.g., 'HR', 'IT', 'Finance')
    - limit: Maximum number of results (1-1000)
    - offset: Number of results to skip for pagination
    """
    Config = get_config()  # Add this line
    UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()  # Add this line
    
    session = Config.get_session()
    try:
        # Validate status
        valid_statuses = ['pending', 'processed']
        if status and status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Validate department
        if dept and dept not in Config.DEPARTMENTS:
            raise HTTPException(status_code=400, detail="Invalid department specified")
        
        query = session.query(UserQuestion)
        
        if status:
            query = query.filter(UserQuestion.status == status)
        if dept:
            query = query.filter(UserQuestion.dept == dept)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        questions = query.offset(offset).limit(limit).all()
        
        result = [
            {
                "id": str(q.id),
                "query": q.query,
                "answer": q.answer,
                "context": q.context,
                "department": q.dept.value if q.dept else None,
                "status": q.status.value if q.status else None,
                "createdAt": q.createdat.isoformat() if q.createdat else None
            }
            for q in questions
        ]
        
        return {
            "questions": result,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "requested_by": admin_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

@router.get("/getadminquestions")
async def get_admin_questions(
    status: str | None = Query(None),
    dept: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),  # Add pagination
    offset: int = Query(0, ge=0),
    admin_id: str = Depends(get_admin_id_from_token)  # Validate admin token
):
    """
    Retrieve admin questions based on status and department.
    - status: Filter by question status (e.g., 'pending', 'processed')
    - dept: Filter by department (e.g., 'HR', 'IT', 'Finance')
    - limit: Maximum number of results (1-1000)
    - offset: Number of results to skip for pagination
    """
    Config = get_config()  # Add this line
    UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()  # Add this line
    
    session = Config.get_session()
    try:
        # Validate status
        valid_statuses = ['pending', 'processed']
        if status and status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Validate department
        if dept and dept not in Config.DEPARTMENTS:
            raise HTTPException(status_code=400, detail="Invalid department specified")
        
        query = session.query(AdminQuestion)
        
        if status:
            query = query.filter(AdminQuestion.status == status)
        if dept:
            query = query.filter(AdminQuestion.dept == dept)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        questions = query.offset(offset).limit(limit).all()
        
        result = [
            {
                "id": str(q.id),
                "adminid": str(q.adminid) if q.adminid else None,
                "question": q.question,
                "answer": q.answer if q.answer else None,
                "department": q.dept.value if q.dept else None,
                "status": q.status.value if q.status else None,
                "frequency": q.frequency,
                "vectordbid": str(q.vectordbid) if q.vectordbid else None,
                "createdAt": q.createdat.isoformat() if q.createdat else None
            }
            for q in questions
        ]
        
        return {
            "questions": result,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "requested_by": admin_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

@router.post("/answer")
async def answer_admin_question(
    question_id: str = Body(..., embed=True),
    answer: str = Body(..., embed=True),
    admin_id: str = Depends(get_admin_id_from_token)  # Get admin_id from token
):
    """
    Store the answer to an admin question and mark it as processed.
    - question_id: The ID of the admin question to be answered
    - answer: The answer text
    """
    UploadService = get_upload_service()  # Add this line
    UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()  # Add this line
    Config = get_config()  # Add this line
    session = Config.get_session()
    try:
        # Validate inputs
        if not question_id or not question_id.strip():
            raise HTTPException(status_code=400, detail="Question ID is required")
        
        if not answer or not answer.strip():
            raise HTTPException(status_code=400, detail="Answer cannot be empty")
        
        if len(answer.strip()) < 10:
            raise HTTPException(status_code=400, detail="Answer must be at least 10 characters")

        # Validate UUID
        try:
            q_id = UUID(question_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid question_id format")

        # Validate admin_id from token
        try:
            admin_uuid = UUID(admin_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid admin ID from token")

        # Fetch the admin question
        admin_question = session.query(AdminQuestion).filter(AdminQuestion.id == q_id).first()
        if not admin_question:
            raise HTTPException(status_code=404, detail="Admin question not found")
        
        # Check if question is already processed
        if admin_question.status == AdminQuestionStatus.processed:
            raise HTTPException(status_code=400, detail="Question is already processed")
        
        # Convert department enum to string for upload service
        dept_str = admin_question.dept.value if admin_question.dept else "General"
        
        # Call upload_answer and handle the response properly
        upload_result = await UploadService.upload_answer(
            admin_question.question, 
            answer, 
            dept_str, 
            str(admin_question.id)
        )
        
        # Check if upload was successful
        if "error" in upload_result:
            raise HTTPException(status_code=500, detail=f"Vector DB error: {upload_result['error']}")
        
        # Extract the document_id from the response
        vector_document_id = upload_result.get("document_id")
        if not vector_document_id:
            raise HTTPException(status_code=500, detail="No document ID returned from vector database")

        # Update the answer and status
        admin_question.answer = answer.strip()
        admin_question.status = AdminQuestionStatus.processed
        admin_question.vectordbid = UUID(vector_document_id)
        admin_question.adminid = admin_uuid  # Set the answering admin

        session.commit()

        return {
            "success": True, 
            "message": "Answer stored and question marked as processed",
            "vector_id": vector_document_id,
            "question_id": str(admin_question.id),
            "answered_by": admin_id
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

@router.post("/purge/all")
async def purge_all_data(
    secret_password: str = Body(..., embed=True),
    confirmation: str = Body(..., embed=True),
    admin_id: str = Depends(get_admin_id_from_token)
):
    """
    DANGER: Purge ALL data from vector database and PostgreSQL database.
    This action is IRREVERSIBLE and will delete ALL stored data.
    
    - secret_password: Must be "bhamakhanda"
    - confirmation: Must be "DELETE_ALL_DATA_PERMANENTLY"
    - Requires admin authentication
    """
    Config = get_config()
    UploadService = get_upload_service()
    UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()
    
    # Validate secret password
    if secret_password != "bhamakhanda":
        raise HTTPException(status_code=403, detail="Invalid secret password")
    
    # Validate confirmation
    if confirmation != "DELETE_ALL_DATA_PERMANENTLY":
        raise HTTPException(status_code=400, detail="Invalid confirmation. Must be 'DELETE_ALL_DATA_PERMANENTLY'")
    
    session = Config.get_session()
    purge_results = {
        "success": False,
        "vector_db_purged": False,
        "postgres_purged": False,
        "errors": [],
        "purged_by": admin_id,
        "timestamp": None
    }
    
    try:
        from datetime import datetime
        purge_results["timestamp"] = datetime.utcnow().isoformat()
        
        print(f"🚨 DANGER: Starting complete data purge by admin {admin_id}")
        
        # Step 1: Purge Vector Database
        try:
            print("🔥 Purging Vector Database...")
            
            # Create instance of UploadService and call the method
            upload_service = UploadService()
            vector_result = await upload_service.purge_all_vectors()
            
            if vector_result.get("success", False):
                purge_results["vector_db_purged"] = True
                purge_results["vector_details"] = vector_result.get("deletion_details", [])
                print("✅ Vector database purged successfully")
            else:
                error_msg = f"Vector DB purge failed: {vector_result.get('message', 'Unknown error')}"
                purge_results["errors"].append(error_msg)
                purge_results["errors"].extend(vector_result.get("errors", []))
                print(f"❌ {error_msg}")
                
        except Exception as e:
            error_msg = f"Vector database purge exception: {str(e)}"
            purge_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        # Step 2: Purge PostgreSQL Database
        try:
            print("🔥 Purging PostgreSQL Database...")
            
            # Delete all records from all tables (order matters due to foreign keys)
            tables_to_purge = [
                (UserQuestion, "user_questions"),
                (AdminQuestion, "admin_questions"), 
                (TextKnowledge, "text_knowledge")
            ]
            
            purged_counts = {}
            
            for model_class, table_name in tables_to_purge:
                try:
                    # Count records before deletion
                    count_before = session.query(model_class).count()
                    
                    # Delete all records
                    deleted_count = session.query(model_class).delete()
                    
                    purged_counts[table_name] = {
                        "before": count_before,
                        "deleted": deleted_count
                    }
                    
                    print(f"🗑️  Purged {deleted_count} records from {table_name}")
                    
                except Exception as e:
                    error_msg = f"Failed to purge {table_name}: {str(e)}"
                    purge_results["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Commit all database changes
            session.commit()
            purge_results["postgres_purged"] = True
            purge_results["purged_counts"] = purged_counts
            
            print("✅ PostgreSQL database purged successfully")
            
        except Exception as e:
            session.rollback()
            error_msg = f"PostgreSQL purge exception: {str(e)}"
            purge_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        # Step 3: Clean up file system (optional)
        try:
            import shutil
            
            # Clean up documents directory if it exists
            if hasattr(Config, 'DOCUMENTS_PATH') and Config.DOCUMENTS_PATH:
                docs_path = Config.DOCUMENTS_PATH
                if os.path.exists(docs_path):
                    deleted_files = []
                    # Remove all files in documents directory
                    for filename in os.listdir(docs_path):
                        file_path = os.path.join(docs_path, filename)
                        if os.path.isfile(file_path):
                            try:
                                os.remove(file_path)
                                deleted_files.append(filename)
                                print(f"🗑️  Deleted file: {filename}")
                            except Exception as file_error:
                                error_msg = f"Failed to delete file {filename}: {str(file_error)}"
                                purge_results["errors"].append(error_msg)
                                print(f"❌ {error_msg}")
                    
                    purge_results["documents_cleaned"] = True
                    purge_results["deleted_files"] = deleted_files
                    
        except Exception as e:
            error_msg = f"File system cleanup failed: {str(e)}"
            purge_results["errors"].append(error_msg)
            print(f"⚠️  {error_msg}")
        
        # Determine overall success
        if purge_results["vector_db_purged"] and purge_results["postgres_purged"]:
            purge_results["success"] = True
            print("🎉 Complete data purge successful!")
        else:
            print("⚠️  Partial purge completed with errors")
        
        return purge_results
        
    except Exception as e:
        session.rollback()
        error_msg = f"Critical purge failure: {str(e)}"
        purge_results["errors"].append(error_msg)
        print(f"💥 {error_msg}")
        
        raise HTTPException(status_code=500, detail=f"Purge operation failed: {str(e)}")
        
    finally:
        session.close()

@router.post("/purge/vector-only")
async def purge_vector_db_only(
    secret_password: str = Body(..., embed=True),
    admin_id: str = Depends(get_admin_id_from_token)
):
    """
    Purge ONLY the vector database, keeping PostgreSQL data intact.
    This will remove all embeddings and vector search capabilities.
    
    - secret_password: Must be "bhamakhanda"
    """
    if secret_password != "bhamakhanda":
        raise HTTPException(status_code=403, detail="Invalid secret password")
    
    UploadService = get_upload_service()
    
    try:
        from datetime import datetime
        
        print(f"🔥 Purging Vector Database only by admin {admin_id}")
        
        # Create instance and purge only vector database
        upload_service = UploadService()
        vector_result = await upload_service.purge_all_vectors()
        
        if vector_result.get("success", False):
            return {
                "success": True,
                "message": "Vector database purged successfully",
                "postgres_intact": True,
                "purged_by": admin_id,
                "timestamp": datetime.now().isoformat(),
                "vector_details": vector_result.get("deletion_details", []),
                "deleted_count": vector_result.get("deleted_count", 0)
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Vector database purge failed: {vector_result.get('message', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector purge failed: {str(e)}")

@router.get("/purge/status")
async def get_purge_status(
    admin_id: str = Depends(get_admin_id_from_token)
):
    """
    Get current database status - record counts for monitoring purge effects.
    """
    Config = get_config()
    UploadService = get_upload_service()
    UserQuestion, AdminQuestion, TextKnowledge, DeptType, AdminQuestionStatus = get_models()
    
    session = Config.get_session()
    
    try:
        from datetime import datetime
        
        # Count records in each table
        user_questions_count = session.query(UserQuestion).count()
        admin_questions_count = session.query(AdminQuestion).count()
        text_knowledge_count = session.query(TextKnowledge).count()
        
        # Get vector database status (if available)
        vector_status = {"status": "unknown", "count": 0}
        try:
            upload_service = UploadService()
            vector_result = await upload_service.get_vector_count()
            if vector_result.get("success"):
                vector_status = {
                    "status": "active",
                    "count": vector_result.get("count", 0),
                    "collection_details": vector_result.get("collection_details", [])
                }
        except Exception as e:
            vector_status = {"status": f"error: {str(e)}", "count": 0}
        
        return {
            "database_status": {
                "user_questions": user_questions_count,
                "admin_questions": admin_questions_count,
                "text_knowledge": text_knowledge_count,
                "total_postgres_records": user_questions_count + admin_questions_count + text_knowledge_count
            },
            "vector_database": vector_status,
            "checked_by": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
        
    finally:
        session.close()