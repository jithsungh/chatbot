from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Query, Depends
from uuid import uuid4,UUID
from typing import Optional, List
import asyncio
import os
import logging

logger = logging.getLogger("delete_file_logger")
logging.basicConfig(level=logging.INFO)

from src.service import UploadService

from src.config import Config

from src.admin.filter import QuestionFilter

from .UserRoutes import department_router

# Role-based authentication
from src.dependencies.role_auth import require_admin_or_above, get_admin_id_from_admin
from src.models.admin import Admin

from src.models import UserQuestion, AdminQuestion, TextKnowledge, FileKnowledge, Department, DeptKeyword
from src.models.dept_failure import DeptFailure, DeptFailureStatus
from src.models.user_question import DeptType
from src.models.admin_question import AdminQuestionStatus

router = APIRouter() 

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


@router.post("/upload/files/{dept}")
async def upload_files(
    dept: str,
    files: list[UploadFile] = File(...),
    current_admin: Admin = Depends(require_admin_or_above),
    concurrent_limit: int = Query(3, ge=1, le=5, description="Number of files to process concurrently")
):
    """
    Unified endpoint to upload single or multiple files.
    Each file is processed via UploadService and recorded in FileKnowledge.
    """


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

            file_path = await UploadService.upload_file(file, dept, str(file_uuid))
            if isinstance(file_path, dict) and "error" in file_path:
                raise Exception(file_path["error"])

            from src.models.user_question import DeptType            
            record = FileKnowledge.create(
                session=session,
                adminid=current_admin.id,
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
        "uploaded_by": str(current_admin.id)
    }

# upload text knowledge
@router.post("/upload/text/{dept}")
async def upload_text(
    dept: str,
    title: str = Body(..., embed=True),
    text: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_admin_or_above)
):
    """Upload raw text to be processed and stored in the vector database."""
    
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
          # Get admin UUID from current admin
        admin_uuid = current_admin.id
        
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
        result = await UploadService.upload_text(text, dept, title, str(text_knowledge.id))
        
        # Check if vector processing was successful
        if "error" in result:            
            return {
                "success": True,
                "message": "Text stored in database but vector processing failed",
                "database_id": str(text_knowledge.id),
                "vector_error": result["error"],
                "uploaded_by": str(current_admin.id)
            }
        return {
            "success": True,
            "message": "Text successfully stored in database and vector database",
            "database_id": str(text_knowledge.id),
            "result": result,
            "uploaded_by": str(current_admin.id)
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
    current_admin: Admin = Depends(require_admin_or_above)  # Validate admin token
):
    """
    Summarize pending admin questions using the QuestionFilter service.
    """
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
        result["processed_by"] = str(current_admin.id)
        
        return result
        
    except Exception as e:
        print(f"❌ Test pipeline failed: {e}")        
        return {
            "success": False, 
            "errors": [str(e)],
            "processed_by": str(current_admin.id)
        }
    finally:
        session.close()

# answer to questions
@router.post("/answer")
async def answer_admin_question(
    question_id: str = Body(..., embed=True),
    answer: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_admin_or_above)  # Get admin from token
):
    """
    Store the answer to an admin question and mark it as processed.
    - question_id: The ID of the admin question to be answered
    - answer: The answer text
    """
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
            raise HTTPException(status_code=400, detail="Invalid question_id format")        # Get admin UUID from current admin
        admin_uuid = current_admin.id

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
            "answered_by": str(current_admin.id)
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_admin: Admin = Depends(require_admin_or_above),
    debug: bool = Query(False, description="Set true to enable verbose debug logging")
):
    session = Config.get_session()
    try:
        # Validate UUID
        try:
            f_id = UUID(file_id)
            if debug: logger.info(f"Validated file_id: {f_id}")
        except ValueError:
            logger.error(f"Invalid file_id format: {file_id}")
            raise HTTPException(status_code=400, detail="Invalid file_id format")
        
        # Fetch record
        file_record = session.query(FileKnowledge).filter(FileKnowledge.id == f_id).first()
        if not file_record:
            logger.warning(f"File record not found for ID: {f_id}")
            raise HTTPException(status_code=404, detail="File knowledge record not found")
        
        if debug: logger.info(f"Found file record: {file_record.file_path}")
        
        # Delete physical file
        if os.path.exists(file_record.file_path):
            try:
                os.remove(file_record.file_path)
                if debug: logger.info(f"Deleted physical file: {file_record.file_path}")
            except Exception as e:
                logger.error(f"Failed to delete physical file {file_record.file_path}: {e}")
        
        # Delete vectors from vectorDB
        try:
            result = UploadService.delete_vectors_by_knowledge_id(str(file_record.id))
            if debug: logger.info(f"Deleted vectors from vectorDB: {result}")
        except Exception as e:
            logger.error(f"Failed to delete vectors from vectorDB: {e}")
        
        # Delete DB record
        try:
            session.delete(file_record)
            session.commit()
            if debug: logger.info(f"Deleted DB record for file_id: {file_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete DB record: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete DB record: {e}")
        
        return {
            "success": True,
            "message": "File knowledge record and associated file deleted",
            "file_id": file_id,
            "deleted_by": str(current_admin.id)
        }
    
    except HTTPException as e:
        raise
    except Exception as e:
        session.rollback()
        logger.exception(f"Unexpected error deleting file_id {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        session.close()
        if debug: logger.info("Session closed.")

# delete text by id
@router.delete("/text/{text_id}")
async def delete_text_knowledge(
    text_id: str,
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Delete a text knowledge record by ID:
      - Remove record from DB
      - Delete associated vector embeddings
    """
    session = Config.get_session()

    try:
        # Validate UUID
        try:
            t_id = UUID(text_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid text_id format")

        # Fetch record
        text_record = session.query(TextKnowledge).filter(TextKnowledge.id == t_id).first()
        if not text_record:
            raise HTTPException(status_code=404, detail="Text knowledge record not found")

        # Delete associated vectors
        vec_result = UploadService.delete_vectors_by_knowledge_id(str(text_record.id))

        # Delete DB record
        session.delete(text_record)
        session.commit()

        return {
            "success": True,
            "message": "Text knowledge deleted successfully",
            "vector_deleted": vec_result
        }

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

@router.put("/text/{text_id}")
async def edit_text_knowledge(
    text_id: str,
    title: Optional[str] = Body(None, embed=True),
    text: Optional[str] = Body(None, embed=True),
    dept: Optional[str] = Body(None, embed=True),
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Edit an existing text knowledge record:
      - Update title, text, and/or department in DB
      - Delete old vector embeddings and re-upload if text changed
      - If only title changed, just update DB
      - If only dept changed, update DB (and optionally vector metadata)
    """
    session = Config.get_session()
    
    try:
        # Validate UUID
        try:
            t_id = UUID(text_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid text_id format")
        
        # Fetch record
        text_record = session.query(TextKnowledge).filter(TextKnowledge.id == t_id).first()
        if not text_record:
            raise HTTPException(status_code=404, detail="Text knowledge record not found")
        
        # Track what changed
        updated_fields = {}
        text_changed = False
        
        if title is not None and title != text_record.title:
            updated_fields["title"] = title
            text_record.title = title
        
        if text is not None and text != text_record.text:
            updated_fields["text"] = text
            text_record.text = text
            text_changed = True
        
        if dept is not None:
            # Validate department
            try:
                from src.models.user_question import DeptType
                dept_enum = DeptType(dept)
                if dept_enum != text_record.dept:
                    updated_fields["dept"] = dept_enum
                    text_record.dept = dept_enum
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid department specified")
        
        if not updated_fields:
            return {"message": "No changes detected"}
        
        session.commit()  # Save updated DB record
        
        vec_result = None
        vec_upload_result = None
        
        if text_changed:
            # Delete old vectors
            vec_result = UploadService.delete_vectors_by_knowledge_id(str(text_record.id))
            # Re-upload new text vectors
            vec_upload_result = await UploadService.upload_text(
                text=text_record.text,
                dept=text_record.dept,
                title=text_record.title,
                text_uuid=str(text_record.id)
            )
        
        return {
            "success": True,
            "message": "Text knowledge updated successfully",
            "updated_fields": list(updated_fields.keys()),
            "vector_deleted": vec_result if text_changed else None,
            "vector_uploaded": vec_upload_result if text_changed else None
        }
    
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()

# -----------------------
# Add keywords
# -----------------------
@router.post("/departments/keywords")
async def add_keywords(
    dept_name: str = Body(..., embed=True),
    keywords: List[str] = Body(..., embed=True),
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Add one or multiple keywords to a department.
    """
    session = Config.get_session()
    try:
        dept_enum = validate_department(dept_name)
        department = session.query(Department).filter(Department.name == dept_enum).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        added_keywords = []
        for kw in keywords:
            kw = kw.strip()
            if not kw:
                continue
            keyword_record = DeptKeyword.create(session=session, dept_id=department.id, keyword=kw)
            added_keywords.append({"id": str(keyword_record.id), "keyword": kw})

        session.commit()        

        return {
            "success": True,
            "department": dept_name,
            "added_keywords": added_keywords,
            "added_by": str(current_admin.id)
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        department_router.refresh_data_from_database()
        session.close()


# -----------------------
# Edit keyword
# -----------------------
@router.put("/departments/keywords/{keyword_id}")
async def edit_keyword(
    keyword_id: str,
    new_keyword: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Update the value of an existing keyword.
    """
    session = Config.get_session()
    try:
        try:
            kw_id = UUID(keyword_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid keyword_id format")

        keyword_record = session.query(DeptKeyword).filter(DeptKeyword.id == kw_id).first()
        if not keyword_record:
            raise HTTPException(status_code=404, detail="Keyword not found")

        keyword_record.keyword = new_keyword.strip()
        session.commit()        


        return {
            "success": True,
            "keyword_id": keyword_id,
            "new_keyword": keyword_record.keyword,
            "updated_by": str(current_admin.id)
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
        # refresh department_router data
        department_router.router.refresh_data_from_database()


# -----------------------
# Delete keyword
# -----------------------
@router.delete("/departments/keywords/{keyword_id}")
async def delete_keyword(
    keyword_id: str,
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Delete a department keyword by its ID.
    """
    session = Config.get_session()
    try:
        try:
            kw_id = UUID(keyword_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid keyword_id format")

        keyword_record = session.query(DeptKeyword).filter(DeptKeyword.id == kw_id).first()
        if not keyword_record:
            raise HTTPException(status_code=404, detail="Keyword not found")

        session.delete(keyword_record)
        session.commit()  

        return {
            "success": True,
            "keyword_id": keyword_id,
            "deleted_by": str(current_admin.id)
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
        # refresh department_router data
        department_router.refresh_data_from_database()      

# edit description
@router.put("/departments/{dept_name}")
async def edit_department_description(
    dept_name: str,
    new_description: str = Body(..., embed=True),
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Update the description of a department.
    """
    session = Config.get_session()
    try:
        dept_enum = validate_department(dept_name)
        department = session.query(Department).filter(Department.name == dept_enum).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        department.description = new_description.strip()
        session.commit()        
        return {
            "success": True,
            "department": dept_name,
            "new_description": department.description,
            "updated_by": str(current_admin.id)
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

# close dept failure
@router.put("/departments/failures")
async def close_department_failure(
    failure_id: str = Body(..., embed=True),
    comments: Optional[str] = Body(None, embed=True),
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Mark a department failure as processed (closed) with optional comments.
    """
    session = Config.get_session()
    try:
        # Validate UUID
        try:
            f_id = UUID(failure_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid failure_id format")

        # Fetch the failure record
        failure_record = session.query(DeptFailure).filter(DeptFailure.id == f_id).first()
        if not failure_record:
            raise HTTPException(status_code=404, detail="Failure record not found")

        # Check if already processed
        if failure_record.status == DeptFailureStatus.processed:
            raise HTTPException(status_code=400, detail="Failure is already processed")

        # Update status
        failure_record.status = DeptFailureStatus.processed
        if comments:
            failure_record.comments = comments.strip()
        failure_record.adminid = current_admin.id

        session.commit()

        return {
            "success": True,
            "failure_id": failure_id,
            "status": failure_record.status.value,
            "closed_by": str(current_admin.id),
            "comments": failure_record.comments,
        }

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

# discard dept failure
@router.put("/departments/failures/discard")
async def discard_department_failure(
    failure_id: str = Body(..., embed=True),
    comments: Optional[str] = Body(None, embed=True),
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Mark a department failure as discarded with optional comments.
    """
    session = Config.get_session()
    try:
        # Validate UUID
        try:
            f_id = UUID(failure_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid failure_id format")

        # Fetch the failure record
        failure_record = session.query(DeptFailure).filter(DeptFailure.id == f_id).first()
        if not failure_record:
            raise HTTPException(status_code=404, detail="Failure record not found")

        # Check if already discarded
        if failure_record.status == DeptFailureStatus.discarded:
            raise HTTPException(status_code=400, detail="Failure is already discarded")

        # Update status
        failure_record.status = DeptFailureStatus.discarded
        if comments:
            failure_record.comments = comments.strip()
        failure_record.adminid = current_admin.id

        session.commit()

        return {
            "success": True,
            "failure_id": failure_id,
            "status": failure_record.status.value,
            "discarded_by": str(current_admin.id),
            "comments": failure_record.comments,
        }

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()



# purge user history older than given time , default 24hrs
@router.delete("/history/purge")
async def purge_user_history(
    time_hours: int = Query(24, ge=1, le=168, description="Purge history older than this many hours (1-168)"),
):
    """
    Purge user conversation history older than the specified number of hours.
    Default is 24 hours, max is 168 hours (7 days).
    """
    historyManager = Config.HISTORY_MANAGER
    try:
        deleted_count = historyManager.purge_old_context(older_than_hours=time_hours)
        return {
            "success": True,
            "message": f"Purged {deleted_count} history records older than {time_hours} hours"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

# ...existing code...

@router.post("/refresh-router-data")
async def refresh_router_data(
    current_admin: Admin = Depends(require_admin_or_above)
):
    """
    Refresh department routing data from database.
    Requires admin role or above.
    """
    try:

        # Refresh router data
        success = department_router.router.refresh_data_from_database()
        
        if success:
            # Get updated summary
            summary = department_router.router.get_data_summary()

            return {
                "message": "Router data refreshed successfully",
                "success": True,
                "data_summary": summary,
                "refreshed_by": str(current_admin.id),
                "admin_name": current_admin.name
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to refresh router data from database"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing router data: {str(e)}"
        )



