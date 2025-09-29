from fastapi import APIRouter, HTTPException, Body, Depends
from src.inference.Pipeline import Pipeline
from src.inference.HybridRouter import HybridDepartmentRouter
from src.admin.avg_response_cal import AvgResponseTimeCalculator
from src.config import Config
import time
# Role-based authentication
from src.dependencies.role_auth import require_read_only_or_above
from src.models.admin import Admin


router= APIRouter()

pipeline = Pipeline()
historyManager = Config.HISTORY_MANAGER
department_router = HybridDepartmentRouter()
avg_response_cal = AvgResponseTimeCalculator()


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
        start = time.perf_counter()
        response = await pipeline.process_user_query(query,userid)
        end = time.perf_counter()
        time_taken = end-start
        avg_response_cal.store_response_time(time_taken)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/department")
async def get_department(
    query: str = Body(..., embed=True, example="What is Techmojo?"),
    current_admin: Admin = Depends(require_read_only_or_above),
):
    """
    Determine the department for a given query.
    Requires read-only admin access or above.
    - query: The user's question or input
    """
    if not query:
        raise HTTPException(status_code=400, detail="'query' is required")

    try:
        department = department_router.route_query(query)
        return {
            "department": department,
            "requested_by": str(current_admin.id)
        }
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