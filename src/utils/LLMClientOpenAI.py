### this is gpt client
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import time

from src.config import Config

class LLMClientOpenAI:
    def __init__(self):
        """Initialize Groq LLM"""
        try:
            api_key = Config.GROQ_API_KEY
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.llm = ChatGroq(
                api_key=api_key,
                model="openai/gpt-oss-120b",
                temperature=0.1,
                max_tokens=1024
            )
            print("✅ Connected to Groq LLM")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            raise
    
    def get_response(self, prompt: str) -> str:
        """Get response from Groq LLM"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response
        except Exception as e:
            print(f"❌ LLM prediction failed: {e}")
            raise

# if __name__ == "__main__":
#     client = LLMClientOpenAI()
#     test_prompt = client.generate_prompt(
#         query="What is Techmojo?",
#         context_text="Techmojo Solutions Pvt Ltd is a technology company specializing in AI and cloud solutions.",
#         history_text="User: Hi\nAI: Hello! How can I assist you today?"
#     )
#     print("started getting response")
#     print("##############################################")
#     start = time.time()
#     response = client.get_response(test_prompt)
#     end = time.time()
#     print(f"Time taken: {end - start} seconds")
#     print("##############################################")
#     print("LLM Response:", response)
#     print("##############################################")
#     print("LLM Response content:", response.content)


# if __name__ == "__main__":
#     client = LLMClient()

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
#     for iteration in range(1,5):
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


            
    