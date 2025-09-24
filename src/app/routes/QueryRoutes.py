from fastapi import APIRouter,HTTPException,Body
from src.inference.Pipeline import Pipeline

router= APIRouter()

pipeline = Pipeline()

@router.post("/query/")
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