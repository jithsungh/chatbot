import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_default_api_key")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your_default_google_api_key")
    DEPARTMENTS = os.getenv("DEPARTMENTS", "HR, IT, Security").strip().split(',')
    ORGANIZATION = os.getenv("ORGANIZATION", "Techmojo Solutions Pvt Ltd")


# print("GROQ_API_KEY:", Config.GROQ_API_KEY, "Type:", type(Config.GROQ_API_KEY))
# print("DEPARTMENTS:", Config.DEPARTMENTS, "Type:", type(Config.DEPARTMENTS))
# print("ORGANIZATION:", Config.ORGANIZATION, "Type:", type(Config.ORGANIZATION))
