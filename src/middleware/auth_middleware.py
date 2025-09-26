from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from uuid import UUID

from src.config import Config

class TokenValidationMiddleware:
    def __init__(self):
        self.secret_key = Config.SECRET_KEY
        self.algorithm = "HS256"
        self.security = HTTPBearer()

    def validate_token(self, token: str) -> dict:
        """
        Validate JWT token and return payload with admin_id
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Payload containing admin_id and other claims
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decode the JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Extract admin_id from payload
            admin_id: str = payload.get("sub")
            if admin_id is None:
                raise credentials_exception
            
            # Validate admin_id format (should be UUID)
            try:
                UUID(admin_id)
            except ValueError:
                raise credentials_exception
            
            # Return the full payload
            return {
                "admin_id": admin_id,
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "payload": payload
            }
            
        except JWTError as e:
            print(f"JWT Error: {e}")
            raise credentials_exception
        except Exception as e:
            print(f"Token validation error: {e}")
            raise credentials_exception

    def extract_token_from_header(self, authorization: str) -> str:
        """
        Extract token from Authorization header
        
        Args:
            authorization: Authorization header value (e.g., "Bearer token_here")
            
        Returns:
            str: JWT token
            
        Raises:
            HTTPException: If header format is invalid
        """
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return parts[1]

    def validate_request_token(self, request: Request) -> dict:
        """
        Validate token from request and return payload
        
        Args:
            request: FastAPI Request object
            
        Returns:
            dict: Token payload with admin_id
        """
        authorization = request.headers.get("Authorization")
        token = self.extract_token_from_header(authorization)
        return self.validate_token(token)

# Create global instance
token_validator = TokenValidationMiddleware()