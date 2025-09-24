from sentence_transformers import SentenceTransformer, util
from collections import Counter
import re
from src.config import Config

class HybridDepartmentRouter:
    """
    Combines embeddings for semantic understanding with domain-specific keywords.
    Works for new queries intelligently while retaining high accuracy for known domain-specific cases.
    """
    KEYWORDS = {
        "HR": ["hiring", "recruit", "human Resource", "referral", "bonus", "increment", "leave", "vacation", "holiday", "payroll", "salary", "benefits", "recruitment", "promotion", "tax", "attendance", "visa", "emergency contact", "remote work", "work from home", "spouse", "marriage", "insurance", "insurance plan", "work remotely"],
        "IT": ["password", "login", "reset", "asset request", "computer", "network", "email", "vpn", "install", "software", "restore", "webcam", "laptop", "internet", "python", "program", "application", "conflict", "file", "recycle bin", "printer", "printing", "hardware", "driver","network drive", "folder permissions", "sync", "roll back", "app crash", "USB", "drivers", "usb", ],
        "Security": ["security", "breach", "hack", "data leak", "protocol", "vulnerability", "access", "ID card", "id card", "id", "entrance", "phishing", "cameras", "badge", "suspicious", "restricted", "visitor", "register", "entry", "tailgate", "followed", "unauthorized", "unauthorized entry", "intruder", "escort", "report", "incident","contractor", "verify credentials", "BYOD", "personal devices", "parking"]
    }

    def __init__(self):
        self.departments = Config.DEPARTMENTS
        self.department_descriptions = {
            "HR": (
                "Handles all employee-related matters including payroll, salary, benefits, "
                "leave management, vacation policies, attendance, promotions, recruitment, "
                "tax declarations, visas, emergency contact updates, work-from-home approvals, "
                "remote work policies, employee records, and insurance-related inquiries."
            ),
            "IT": (
                "Handles all technical and IT-related issues including password resets, login problems, "
                "software installation and conflicts, application troubleshooting, file recovery, "
                "network connectivity, VPN setup, computer and laptop support, printer setup and maintenance, "
                "hardware issues, driver updates, asset requests, programming environments, and general technical guidance."
            ),
            "Security": (
                "Handles all office safety and security concerns including building access, ID cards, "
                "tailgating prevention, visitor registration, access control, security breaches, "
                "suspicious activities, phishing or data theft incidents, monitoring cameras, "
                "emergency protocols, USB and device safety, intruder alerts, and reporting incidents."
            )
        }

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.department_embeddings = {
            dept: self.model.encode(desc, convert_to_tensor=True)
            for dept, desc in self.department_descriptions.items()
        }
        print("HybridDepartmentRouter initialized with departments:", self.departments)

    def route_query(self, query: str) -> str:
        query_lower = query.lower()
        keyword_scores = Counter()

        # Enhanced Keyword Scoring with n-grams and higher weight for important keywords
        for dept, keywords in self.KEYWORDS.items():
            for kw in keywords:
                # Matching keywords directly
                if re.search(r'\b' + re.escape(kw.lower()) + r'\b', query_lower):
                    keyword_scores[dept] += 2.0  # base keyword match
                # Consider matching 2-word phrases (n-grams)
                if len(kw.split()) == 1:
                    continue
                for n in range(2, len(kw.split()) + 1):
                    ngram = " ".join(kw.split()[:n])
                    if re.search(r'\b' + re.escape(ngram.lower()) + r'\b', query_lower):
                        keyword_scores[dept] += 0.5  # slightly lower weight for n-grams

        # if not keyword_scores:
        #     return "General Inquiry"
        # If no strong keywords matched, force General Inquiry
        strong_keywords_hit = any(score > 0 for score in keyword_scores.values())
        if not strong_keywords_hit:
            return "General Inquiry"


        # Semantic Scoring using embeddings
        query_emb = self.model.encode(query, convert_to_tensor=True)
        semantic_scores = {
            dept: util.cos_sim(query_emb, emb).item()
            for dept, emb in self.department_embeddings.items()
        }

        # Combine keyword scores and semantic scores, adding weights
        combined_scores = {}
        for dept in self.departments:
            combined_scores[dept] = semantic_scores.get(dept, 0) + 1.5 * keyword_scores.get(dept, 0)

        # Dynamically set a threshold for the General Inquiry fallback based on the highest score
        best_dept, best_score = max(combined_scores.items(), key=lambda x: x[1])

        # Adaptive fallback threshold
        if best_score < 0.30:  # you can adjust this based on testing
            return "General Inquiry"

        return best_dept
