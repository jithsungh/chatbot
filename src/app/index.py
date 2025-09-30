from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
import sys
import asyncio
from sqlalchemy import text

from .routes import AdminRoutes
from .routes import UserRoutes
from .routes import AdminAuthRoutes
from .routes import ReadOnlyAdminRoutes
from .routes import SuperAdminRoutes
from src.config import Config


async def startup_health_check():
    """Perform startup health checks before the app starts"""
    print("🔍 Starting health checks...")
    
    # Check PostgreSQL connection
    try:
        print("🔄 Checking PostgreSQL connection...")
        session = Config.get_session()
        
        # Test basic connection
        result = session.execute(text("SELECT 1 as health_check"))
        health_value = result.scalar()
        
        if health_value == 1:
            print("✅ PostgreSQL connection successful")
        else:
            raise Exception("Unexpected health check result")
            
        session.close()
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("🚫 Application startup aborted due to database connection failure")
        sys.exit(1)
    
    # Optional: Check if required tables exist
    try:
        print("🔄 Checking database schema...")
        session = Config.get_session()
        
        # You can add table existence checks here
        # Example: session.execute(text("SELECT 1 FROM your_table_name LIMIT 1"))
        
        session.close()
        print("✅ Database schema check passed")
        
    except Exception as e:
        print(f"⚠️ Database schema check warning: {e}")
        # Don't exit for schema issues, just warn
    
    print("✅ All health checks passed - Starting application...")


app = FastAPI()

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    await startup_health_check()

router = APIRouter()

origins = [
    "http://localhost:5173",   # React local dev
    "http://127.0.0.1:5173",
    "http://localhost:8080",   # Next.js local dev
    "https://chatbot-three-woad-61.vercel.app",  # React prod
    "https://fulsome-unmonopolising-mariela.ngrok-free.dev", # Ngrok tunnel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allowed origins
    allow_credentials=True,           #Allow cookies/auth headers
    allow_methods=["*"],               # Allow all HTTP methods
    allow_headers=["*"],               # Allow all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    """Runtime health check endpoint"""
    try:
        session = Config.get_session()
        result = session.execute(text("SELECT 1"))
        session.close()
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }

app.include_router(UserRoutes.router, prefix="/api/user", tags=["query"])
app.include_router(AdminRoutes.router, prefix="/api/admin", tags=["admin"])
app.include_router(ReadOnlyAdminRoutes.router, prefix="/api/read", tags=["readonlyadmin"])
app.include_router(SuperAdminRoutes.router, prefix="/api/superadmin", tags=["superadmin"])
app.include_router(AdminAuthRoutes.router, prefix="/api/auth", tags=["auth"])