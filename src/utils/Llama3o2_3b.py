# src/utils/LLMClientLlama3_2.py
from llama_cpp import Llama
import time

class LLMClientLlama3_2:
    def __init__(self,
                 model_path: str = "/home/jithsungh/llama_models/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                 n_threads: int = 32,
                 n_ctx: int = 4096,
                 verbose: bool = False):
        print("Initializing LLaMA 3.2 (3B) client...")

        self.model_path = model_path
        self.n_threads = n_threads
        self.n_ctx = n_ctx

        start = time.time()
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_threads=self.n_threads,
                n_ctx=self.n_ctx,
                verbose=verbose
            )                
        except Exception:
            pass
        print(f"Model loaded in {time.time() - start:.2f}s")

    def get_response(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        """
        Return the raw string output from the model.
        """
        out = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            echo=False,
            stop=["</s>"]
        )
        # API returns choices list
        return out["choices"][0]["text"]


# # Example quick test when run directly
# if __name__ == "__main__":
#     client = LLMClientLlama3_2(n_threads=32)
#     test_prompt = """
# You MUST return ONLY a single valid JSON object (start with { and end with }) and nothing else.
# The object keys must be: org_related, has_context, answer, dept, followup, std_question.
# Question: What is 7 times 69?
# """
#     print("Raw answer:")
#     print(client.get_raw(test_prompt, max_tokens=50))
#     print("\nParsed JSON:")
#     print(client.get_json(test_prompt, max_tokens=50))
