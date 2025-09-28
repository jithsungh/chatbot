from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List
from uuid import UUID

from src.middleware.auth_middleware import token_validator
from src.models.admin import Admin, AdminRole
from src.config import Config

security = HTTPBearer()

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Admin:
    """
    Get current admin from token and return full Admin object
    
    Returns:
        Admin: Full admin object with role information
    """
    payload = token_validator.validate_token(credentials.credentials)
    admin_id = payload["admin_id"]
    
    session = Config.get_session()
    try:
        admin = Admin.get_by_id(session, UUID(admin_id))
        if not admin:
            raise HTTPException(
                status_code=401,
                detail="Admin not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not admin.enabled:
            raise HTTPException(
                status_code=403,
                detail="Admin account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return admin
    finally:
        session.close()

def require_roles(allowed_roles: List[AdminRole]):
    """
    Create a dependency that requires specific admin roles
    
    Args:
        allowed_roles: List of AdminRole enums that are allowed to access the endpoint
        
    Returns:
        Function: FastAPI dependency function
    """
    async def role_checker(current_admin: Admin = Depends(get_current_admin)) -> Admin:
        if current_admin.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}. Your role: {current_admin.role.value}"
            )
        return current_admin
    
    return role_checker

# Convenience dependencies for specific roles
async def require_super_admin(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """Require super_admin role"""
    if current_admin.role != AdminRole.superadmin:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Super admin role required. Your role: {current_admin.role.value}"
        )
    return current_admin

async def require_admin_or_above(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """Require admin or super_admin role"""
    if current_admin.role not in [AdminRole.admin, AdminRole.superadmin]:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Admin or super admin role required. Your role: {current_admin.role.value}"
        )
    return current_admin

async def require_read_only_or_above(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """Require read_only, admin, or super_admin role (basically any authenticated admin)"""
    if current_admin.role not in [AdminRole.read_only, AdminRole.admin, AdminRole.superadmin]:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Valid admin role required. Your role: {current_admin.role.value}"
        )
    return current_admin

# Helper function to get admin ID from admin object
def get_admin_id_from_admin(current_admin: Admin = Depends(get_current_admin)) -> str:
    """Get admin ID string from admin object"""
    return str(current_admin.id)
