### this is gemma2-9b-it client
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import time

from src.config import Config


class LLMClientGemma:
    def __init__(self):
        print("Gemma client init")
        """Initialize Groq LLM"""
        try:
            api_key = Config.GROQ_API_KEY
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            start = time.time()
            self.llm = ChatGroq(
                api_key=api_key,
                model="gemma2-9b-it",
                temperature=0.1,
                max_tokens=1024
            )
            end = time.time()
            print(f"Time taken to initialize Gemma model: {end - start} seconds")
            print("✅ Connected to Groq LLM")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            raise

    async def get_response(self, prompt: str) -> str:
        """Get response from Groq LLM"""
        try:
            response = await self.llm.invoke([HumanMessage(content=prompt)])
            return response
        except Exception as e:
            print(f"❌ LLM prediction failed: {e}")
            raise

            