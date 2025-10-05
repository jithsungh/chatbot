from llama_cpp import Llama

class LLMClientGemma:
    def __init__(self, model_path="/home/jithsungh/llama_models/gemma-2-2b-it-Q4_K_M.gguf"):
        try:
            self.llm = Llama(model_path=model_path, n_threads=32, n_batch=512, n_ctx=2048, verbose=False)
            self.llm("Hello", max_tokens=1) # Warm up
            print("✅ Gemma-2 model loaded:", model_path)
        except Exception as e:
            print("❌ Failed to load Gemma-2 model:", e)
            raise

    def get_response(self, prompt):
        try:
            result = self.llm(prompt, max_tokens=256, temperature=0.1, echo=False, stop=["</s>"])
            return result["choices"][0]["text"].strip()
        except Exception as e:
            print("❌ Generation failed:", e)
            raise

# # Usage
# client = LLMClientGemma("/home/jithsungh/llama_models/gemma-2-2b-it-Q4_K_M.gguf")
# response = client.get_response("Explain Techmojo's leave policy in 3 sentences.")
# print(response)
