from fastapi import APIRouter,UploadFile,File,HTTPException,Body


from ...service import UploadService  # Use relative import
from src.config import Config

router= APIRouter()


@router.post("/admin/upload/{dept}")
async def upload_file(
    dept: str,
    file: UploadFile | None = File(None),
    text: str | None = Body(None)
):
    """
    Upload a file or raw text to be processed and stored in the vector database.
    - file: The file to be uploaded (PDF, DOCX, etc.)
    - dept: The department the document belongs to (e.g., HR, IT, Finance)
    - text: Optional raw text input instead of a file
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Either file or text is required")

    if file and text:
        raise HTTPException(status_code=400, detail="Provide either file or text, not both")


    # if text uploaded
    if text:
        if not dept:
            raise HTTPException(status_code=400, detail="No department specified")
        if dept not in Config.DEPARTMENTS:
            raise HTTPException(status_code=400, detail="Invalid department specified")
        
        result=UploadService.upload_text(text,dept)
        return {"result":result}
    # if file uploaded
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    if not dept:
        raise HTTPException(status_code=400, detail="No department specified")
    if dept not in Config.DEPARTMENTS:
        raise HTTPException(status_code=400, detail="Invalid department specified")
    
    result=UploadService.upload_file(file,dept)

    return {"result":result}

# get uploaded files list
@router.get("/admin/upload/list")
async def list_uploaded_files():
    """
    List all uploaded files in the system.
    """
    import os

    upload_dir = "./documents"
    try:
        files = os.listdir(upload_dir)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))