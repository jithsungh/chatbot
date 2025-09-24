### this is Gemini client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import time

from src.config import Config

class LLMClientGoogle:
    def __init__(self):
        """Initialize Google Gemini LLM"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # other params...
            )
            print("✅ Connected to Google Gemini LLM")
        except Exception as e:
            print(f"❌ Failed to initialize Google Gemini LLM: {e}")
            raise
    
    def get_response(self, prompt: str) -> str:
        """Get response from Google Gemini LLM"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response
        except Exception as e:
            print(f"❌ LLM prediction failed: {e}")
            raise

# if __name__ == "__main__":
#     client = LLMClientGoogle()

#     # 5 dummy queries
#     queries = [
#         "What is Techmojo?",
#         "Describe the services offered by Techmojo.",
#         "Who are the key people in Techmojo?",
#         "Where is Techmojo located?",
#         "What technologies does Techmojo use?"
#     ]

#     # Dummy context and history
#     dummy_context = "Techmojo Solutions Pvt Ltd is a technology company specializing in AI and cloud solutions., techmojo was founded in 2010 and is headquartered in San Francisco., Techmojo offers services in AI development, cloud computing, and IT consulting, located in San Francisco."
#     dummy_history = "User: Hi\nAI: Hello! How can I assist you today?"

#     total_times = []

#     # Loop 20 times
#     for iteration in range(1, 5):
#         print(f"\n===== Iteration {iteration} =====")
#         for query in queries:
#             prompt = client.generate_prompt(
#                 query=query,
#                 context_text=dummy_context,
#                 history_text=dummy_history
#             )

#             start = time.time()
#             response = client.get_response(prompt)
#             end = time.time()

#             elapsed = end - start
#             total_times.append(elapsed)

#             print(f"Query: {query}")
#             print(f"Time taken: {elapsed:.3f} seconds")
#             print(f"Response content: {response.content[:100]}...")  # print first 100 chars
#             print("------------------------------------")

#     avg_time = sum(total_times) / len(total_times)
#     print(f"\nTotal LLM invokes: {len(total_times)}")
#     print(f"Average time per LLM call: {avg_time:.3f} seconds")
