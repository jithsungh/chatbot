from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

from src.middleware.auth_middleware import token_validator

security = HTTPBearer()

async def validate_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """
    FastAPI dependency to validate admin token and return payload
    
    Returns:
        dict: Contains admin_id and other token claims
    """
    return token_validator.validate_token(credentials.credentials)

async def get_admin_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    FastAPI dependency to get admin_id from token
    
    Returns:
        str: Admin ID from token
    """
    payload = token_validator.validate_token(credentials.credentials)
    return payload["admin_id"]

async def validate_token_from_request(request: Request) -> Dict[str, str]:
    """
    Validate token directly from request headers
    
    Returns:
        dict: Token payload with admin_id
    """
    return token_validator.validate_request_token(request)