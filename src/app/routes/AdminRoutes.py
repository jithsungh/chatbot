from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Query, Depends
from uuid import uuid4,UUID
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
    from src.models import UserQuestion, AdminQuestion, TextKnowledge, FileKnowledge
    from src.models.user_question import DeptType
    from src.models.admin_question import AdminQuestionStatus
    return UserQuestion, AdminQuestion, TextKnowledge, FileKnowledge, DeptType, AdminQuestionStatus

router = APIRouter()

# Get auth dependencies once
validate_admin_token, get_admin_id_from_token = get_auth_dependencies()


@router.post("/upload/files/{dept}")
async def upload_files(
    dept: str,
    files: list[UploadFile] = File(...),
    admin_id: str = Depends(get_admin_id_from_token),
    concurrent_limit: int = Query(3, ge=1, le=5, description="Number of files to process concurrently")
):
    """
    Unified endpoint to upload single or multiple files.
    Each file is processed via UploadService and recorded in FileKnowledge.
    """
    Config = get_config()
    UploadService = get_upload_service()
    # Suppose you only need FileKnowledge
    _, _, _, FileKnowledge, _ , _= get_models()


    # Validate department
    if dept not in Config.DEPARTMENTS:
        raise HTTPException(status_code=400, detail="Invalid department")
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    max_file_size = 10 * 1024 * 1024
    max_files = 50
    if len(files) > max_files:
        raise HTTPException(status_code=400, detail=f"Max {max_files} files allowed")

    results = []

    async def handle_file(file: UploadFile, index: int):
        file_uuid = uuid4()
        session = Config.get_session()
        try:
            # Optionally, validate file size
            content = await file.read()
            if len(content) > max_file_size:
                raise HTTPException(status_code=413, detail=f"File '{file.filename}' too large")
            await file.seek(0)  # Reset file pointer

            file_path = await UploadService.upload_file(file, dept, file_uuid)
            if isinstance(file_path, dict) and "error" in file_path:
                raise Exception(file_path["error"])

            from src.models.user_question import DeptType
            record = FileKnowledge.create(
                session=session,
                adminid=UUID(admin_id),
                file_name=file.filename,
                file_path=file_path,
                dept=DeptType(dept)
            )

            return {"filename": file.filename, "status": "success", "file_id": str(record.id)}

        except Exception as e:
            session.rollback()
            return {"filename": file.filename, "status": "error", "error": str(e)}
        finally:
            session.close()

    # Process files in batches for concurrency
    for i in range(0, len(files), concurrent_limit):
        batch = files[i:i + concurrent_limit]
        batch_results = await asyncio.gather(*[handle_file(f, i + j) for j, f in enumerate(batch)])
        results.extend(batch_results)

    total_files = len(files)
    successful_uploads = sum(1 for r in results if r["status"] == "success")
    failed_uploads = total_files - successful_uploads

    return {
        "message": f"Processed {total_files} files",
        "successful_uploads": successful_uploads,
        "failed_uploads": failed_uploads,
        "results": results,
        "department": dept,
        "uploaded_by": admin_id
    }

# upload text knowledge
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
        result = await UploadService.upload_text(text, dept, title, text_knowledge.id)
        
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

# summarize pending user questions
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

# answer to questions
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


# delete file by id

# delete text knowledge by id

# ----optional---- last-> edit text functionality

# delete keyword

# add keywords

# edit keyword

# edit description

# upsert vector db with id

# purge user history older than given time , default 24hrs
@router.delete("/history/purge")
async def purge_user_history(
    time_hours: int = Query(24, ge=1, le=168, description="Purge history older than this many hours (1-168)"),
):
    """
    Purge user conversation history older than the specified number of hours.
    Default is 24 hours, max is 168 hours (7 days).
    """
    Config = get_config()
    historyManager = Config.HISTORY_MANAGER
    try:
        deleted_count = historyManager.purge_old_context(older_than_hours=time_hours)
        return {
            "success": True,
            "message": f"Purged {deleted_count} history records older than {time_hours} hours"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



