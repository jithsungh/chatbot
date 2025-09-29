import os
from python_dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import threading
from typing import Optional

from src.inference.HistoryManager import HistoryManager

load_dotenv()

class ModelManager:
    _instance = None
    _instance_lock = threading.Lock()
    _primary_model = None
    _deputy_model = None
    _primary_lock = threading.Lock()
    _deputy_lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def get_primary_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """Get or create the primary sentence transformer model (LAZY LOADED)"""
        if self._primary_model is None:
            with self._primary_lock:
                if self._primary_model is None:
                    # Import here to avoid circular imports
                    from sentence_transformers import SentenceTransformer
                    
                    print(f"🔄 Loading Primary model: {model_name}")
                    try:
                        self._primary_model = SentenceTransformer(model_name)
                        print(f"✅ Primary model loaded successfully")
                    except Exception as e:
                        print(f"❌ Failed to load primary model: {e}")
                        # Return None instead of raising to prevent app crash
                        return None
        return self._primary_model
    
    def get_deputy_model(self, model_name: str = "all-mpnet-base-v2"):
        """Get or create the deputy sentence transformer model (LAZY LOADED)"""
        if self._deputy_model is None:
            with self._deputy_lock:
                if self._deputy_model is None:
                    # Import here to avoid circular imports
                    from sentence_transformers import SentenceTransformer
                    
                    print(f"🔄 Loading Deputy model: {model_name}")
                    try:
                        self._deputy_model = SentenceTransformer(model_name)
                        print(f"✅ Deputy model loaded successfully")
                    except Exception as e:
                        print(f"❌ Failed to load deputy model: {e}")
                        return None
        return self._deputy_model

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_default_api_key")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your_default_google_api_key")

    # Organization & Departments
    ORGANIZATION = os.getenv("ORGANIZATION", "Techmojo Solutions Pvt Ltd")
    DEPARTMENTS = [d.strip() for d in os.getenv("DEPARTMENTS", "HR,IT,Security").split(',')]
    ORGANIZATION_DOMAIN = os.getenv("ORGANIZATION_DOMAIN", "techmojo.in")
    BYPASS_KEY = os.getenv("BYPASS_KEY", "your_bypass_key")

    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
    SECRET_PASSWORD = os.getenv("SECRET_PASSWORD", "bhamakhanda")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # document storage paths
    DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "./documents")
    CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./chromadb")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "TM-DOCS")

    # Database Configuration - Direct Connection (No Lazy Loading)
    POSTGRES_URL = os.getenv("POSTGRES", "postgresql://postgres:1234@localhost:5432/postgres")
    
    # Create engine and session factory immediately
    engine = create_engine(POSTGRES_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)

    # Model configuration
    DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
    DEPUTY_MODEL_NAME = "all-mpnet-base-v2"

    # HISTORY MANAGER
    HISTORY_MANAGER = HistoryManager(max_turns=25)

    @classmethod
    def get_session(cls):
        """Returns a new SQLAlchemy session"""
        return cls.SessionLocal()
    
    @classmethod
    def get_engine(cls):
        """Returns the database engine"""
        return cls.engine
    
    @staticmethod
    def get_embedding_model():
        """Get the shared primary embedding model instance (LAZY LOADED)"""
        model = ModelManager().get_primary_model(Config.DEFAULT_MODEL_NAME)
        if model is None:
            raise RuntimeError("Failed to load primary embedding model")
        return model
    
    @staticmethod
    def get_embedding_model_deputy():
        """Get the shared deputy embedding model instance (LAZY LOADED)"""
        model = ModelManager().get_deputy_model(Config.DEPUTY_MODEL_NAME)
        if model is None:
            raise RuntimeError("Failed to load deputy embedding model")
        return model

    @staticmethod
    def safe_get_embedding_model():
        """Safely get embedding model, returns None if fails (for startup)"""
        try:
            return ModelManager().get_primary_model(Config.DEFAULT_MODEL_NAME)
        except:
            return None

    @staticmethod
    def safe_get_embedding_model_deputy():
        """Safely get deputy embedding model, returns None if fails (for startup)"""
        try:
            return ModelManager().get_deputy_model(Config.DEPUTY_MODEL_NAME)
        except:
            return None

# --- Example Usage ---
# if __name__ == "__main__":
#     # Test SQLAlchemy connection
#     try:
#         session = Config.get_session()
#         result = session.execute("SELECT 1")
#         print("Database connection successful:", result.scalar())
#         session.close()
#     except Exception as e:
#         print("Database connection failed:", e)

#     # Print configuration
#     print("GROQ_API_KEY:", Config.GROQ_API_KEY)
#     print("GOOGLE_API_KEY:", Config.GOOGLE_API_KEY)
#     print("ORGANIZATION:", Config.ORGANIZATION)
#     print("DEPARTMENTS:", Config.DEPARTMENTS)