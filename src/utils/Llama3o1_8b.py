from llama_cpp import Llama

class LLMClientLlama3_1:
    def __init__(self, model_path: str = "/home/jithsungh/llama_models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf", n_threads: int = 32, n_ctx: int = 4096):
        print("Initializing LLaMA 3.1 client")
        try:
            self.llm = Llama(
                model_path=model_path,
                n_threads=n_threads,
                n_ctx=n_ctx,
                verbose=False
            )
            print("✅ Model loaded:", model_path)
        except Exception as e:
            print("❌ Failed to load model:", e)
            raise

    def get_response(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            out = self.llm(
                prompt,
                max_tokens=max_tokens,
                echo=False,
                stop=["</s>"]
            )
            # The API returns something like {"choices": [{"text": "..."}], ...}
            return out["choices"][0]["text"].strip()
        except Exception as e:
            print("❌ Generation failed:", e)
            raise

# if __name__ == "__main__":
#     model_path = "/home/jithsungh/llama_models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
#     client = LLMClientLlama3_1(model_path=model_path, n_threads=32, n_ctx=4096)

#     prompt = """
#     You are a helpful assistant. Answer this in JSON only:
#     {
#       "question": "What is 7 times 69?"
#     }
#     """
#     resp = client.get_response(prompt, max_tokens=50)
#     print("Response:", resp)
