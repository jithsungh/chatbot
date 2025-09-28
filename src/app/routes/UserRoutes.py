from fastapi import APIRouter, HTTPException, Body, Depends
from src.inference.Pipeline import Pipeline
from src.inference.HybridRouter import HybridDepartmentRouter
from src.config import Config

router= APIRouter()

pipeline = Pipeline()
historyManager = Config.HISTORY_MANAGER
department_router = HybridDepartmentRouter()

def get_auth_dependencies():
    from src.dependencies.auth import validate_admin_token, get_admin_id_from_token
    return validate_admin_token, get_admin_id_from_token

# Get auth dependencies once
validate_admin_token, get_admin_id_from_token = get_auth_dependencies()


@router.post("/query")
async def handle_query(
    query: str = Body(..., embed=True, example="What is Techmojo?"),
    userid: str = Body(..., embed=True, example="user123")
):
    """
    Handle user query and return response from the chatbot.
    - query: The user's question or input
    - userid: Unique identifier for the user (for session management)
    """
    if not query or not userid:
        raise HTTPException(status_code=400, detail="Both 'query' and 'userid' are required")

    
    try:
        response = pipeline.process_user_query(query,userid)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/department")
async def get_department(
    query: str = Body(..., embed=True, example="What is Techmojo?"),
    admin_id: str = Depends(get_admin_id_from_token),
):
    """
    Determine the department for a given query.
    - query: The user's question or input
    """
    if not query:
        raise HTTPException(status_code=400, detail="'query' is required")

    try:
    
        department = department_router.route_query(query)
        return {"department": department}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/history/{userid}")
async def clear_history(userid: str):
    """
    Clear conversation history for a specific user.
    - userid: Unique identifier for the user
    """
    if not userid:
        raise HTTPException(status_code=400, detail="'userid' is required")

    try:
        historyManager.clear_history(userid)
        return {"message": f"Conversation history cleared for user {userid}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))