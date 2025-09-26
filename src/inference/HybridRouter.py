from collections import Counter
import re
from typing import Dict, List, Optional

class HybridDepartmentRouter:
    """
    Combines embeddings for semantic understanding with domain-specific keywords.
    Works for new queries intelligently while retaining high accuracy for known domain-specific cases.
    """
    
    # Keywords for each department
    KEYWORDS = {
        "HR": [
            "salary", "payroll", "leave", "vacation", "sick leave", "maternity", "paternity",
            "benefits", "insurance", "health", "dental", "401k", "retirement", "pension",
            "hiring", "recruitment", "onboarding", "offboarding", "termination", "resignation",
            "performance", "review", "appraisal", "promotion", "training", "development",
            "harassment", "discrimination", "complaint", "grievance", "policy", "handbook",
            "employee", "staff", "colleague", "manager", "supervisor", "team lead",
            "contract", "employment", "probation", "full-time", "part-time", "contractor",
            "overtime", "shift", "schedule", "attendance", "time off", "pto", "holiday"
        ],
        
        "IT": [
            "computer", "laptop", "desktop", "monitor", "keyboard", "mouse", "printer",
            "software", "application", "app", "program", "install", "update", "upgrade",
            "password", "login", "access", "account", "credentials", "authentication",
            "network", "wifi", "internet", "connection", "server", "database", "cloud",
            "email", "outlook", "gmail", "attachment", "spam", "phishing",
            "backup", "restore", "file", "folder", "document", "excel", "word", "pdf",
            "virus", "malware", "antivirus", "security", "firewall", "vpn", "remote",
            "troubleshoot", "bug", "error", "crash", "freeze", "slow", "performance",
            "hard drive", "storage", "memory", "ram", "cpu", "hardware", "device"
        ],
        
        "Security": [
            "badge", "access card", "keycard", "entry", "door", "gate", "building",
            "visitor", "guest", "contractor", "vendor", "escort", "registration",
            "camera", "surveillance", "monitoring", "cctv", "recording", "footage",
            "incident", "breach", "unauthorized", "suspicious", "threat", "emergency",
            "evacuation", "fire drill", "safety", "protocol", "procedure", "compliance",
            "parking", "vehicle", "license plate", "traffic", "patrol", "guard",
            "alarm", "alert", "notification", "report", "investigation", "evidence",
            "tailgating", "piggybacking", "social engineering", "phishing", "scam",
            "theft", "vandalism", "trespassing", "assault", "harassment", "violence"
        ]
    }

    def __init__(self):
        # Import Config here to avoid circular imports
        from src.config import Config
        self.departments = Config.DEPARTMENTS
        
        self.department_descriptions = {
            "HR": "Human Resources handles employee relations, benefits, payroll, hiring, training, and workplace policies.",
            "IT": "Information Technology manages computers, software, networks, email, technical support, and cybersecurity.",
            "Security": "Security manages building access, visitor management, surveillance, incident response, and workplace safety.",
            "General Inquiry": "General inquiries about company information, directions, non-specific questions, or topics that don't clearly fit other departments."
        }

        # Lazy initialization of models and embeddings
        self._model = None
        self._department_embeddings = None
        print("HybridDepartmentRouter initialized with departments:", self.departments)

    def _get_model(self):
        """Lazy load the model only when needed"""
        if self._model is None:
            from src.config import Config
            self._model = Config.safe_get_embedding_model()
            if self._model is None:
                print("⚠️ Could not load embedding model, using keyword-only routing")
        return self._model

    def _get_department_embeddings(self):
        """Lazy load department embeddings only when needed"""
        if self._department_embeddings is None:
            model = self._get_model()
            if model is not None:
                try:
                    # Import util here to avoid issues
                    from sentence_transformers import util
                    
                    self._department_embeddings = {}
                    for dept, desc in self.department_descriptions.items():
                        embedding = model.encode(desc, convert_to_tensor=True)
                        self._department_embeddings[dept] = embedding
                    print("✅ Department embeddings loaded")
                except Exception as e:
                    print(f"⚠️ Failed to load department embeddings: {e}")
                    self._department_embeddings = {}
            else:
                self._department_embeddings = {}
        return self._department_embeddings

    def route_query(self, query: str) -> str:
        try:
            # Clean and normalize query
            query_clean = query.lower().strip()
            
            # Method 1: Keyword-based routing (fast and reliable)
            keyword_dept = self._route_by_keywords(query_clean)
            
            # Method 2: Embedding-based routing (if available)
            embedding_dept = self._route_by_embeddings(query) if self._get_model() else None
            
            # Combine results with priority to keyword matching
            if keyword_dept and keyword_dept != "General Inquiry":
                return keyword_dept
            elif embedding_dept and embedding_dept != "General Inquiry":
                return embedding_dept
            else:
                return "General Inquiry"
                
        except Exception as e:
            print(f"❌ Error in route_query: {e}")
            return "General Inquiry"

    def _route_by_keywords(self, query_clean: str) -> Optional[str]:
        """Route query based on keyword matching"""
        try:
            scores = {}
            
            for dept, keywords in self.KEYWORDS.items():
                score = 0
                words_in_query = query_clean.split()
                
                for keyword in keywords:
                    # Exact match
                    if keyword in query_clean:
                        score += 2
                    
                    # Word boundary match
                    if any(keyword in word for word in words_in_query):
                        score += 1
                
                # Normalize by query length
                scores[dept] = score / max(len(words_in_query), 1)
            
            # Find department with highest score
            if scores:
                best_dept = max(scores, key=scores.get)
                best_score = scores[best_dept]
                
                # Threshold for confidence
                if best_score > 0.1:  # Adjust threshold as needed
                    return best_dept
            
            return "General Inquiry"
            
        except Exception as e:
            print(f"❌ Error in keyword routing: {e}")
            return "General Inquiry"

    def _route_by_embeddings(self, query: str) -> Optional[str]:
        """Route query based on embedding similarity"""
        try:
            model = self._get_model()
            department_embeddings = self._get_department_embeddings()
            
            if not model or not department_embeddings:
                return None
                
            # Import util here
            from sentence_transformers import util
            
            # Get query embedding
            query_embedding = model.encode(query, convert_to_tensor=True)
            
            # Calculate similarities
            similarities = {}
            for dept, dept_embedding in department_embeddings.items():
                similarity = util.pytorch_cos_sim(query_embedding, dept_embedding)[0][0].item()
                similarities[dept] = similarity
            
            # Find best match
            if similarities:
                best_dept = max(similarities, key=similarities.get)
                best_similarity = similarities[best_dept]
                
                # Threshold for confidence (adjust as needed)
                if best_similarity > 0.3:
                    return best_dept
            
            return "General Inquiry"
            
        except Exception as e:
            print(f"❌ Error in embedding routing: {e}")
            return None