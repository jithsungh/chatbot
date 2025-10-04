from llama_cpp import Llama

class LLMClientPhi3:
    def __init__(self):
        print("Phi-3 Mini client init")
        """Initialize Phi-3 Mini Q4 LLM"""
        try:
            # Load once (big init cost, keep global/singleton)
            self.llm = Llama(
                model_path="/home/jithsungh/llama_models/Phi-3-mini-4k-instruct-q4.gguf",  # Update to your path
                n_threads=32,       # Adjust based on your CPU
                n_ctx=4096,         # Max context size for this model
                verbose=False
            )
            print("✅ Phi-3 Mini model loaded")
        except Exception as e:
            print(f"❌ Failed to initialize Phi-3 Mini: {e}")
            raise

    def get_response(self, prompt: str, max_tokens: int = 512) -> str:
        """Get response from Phi-3 Mini LLM"""
        try:
            result = self.llm(
                prompt,
                max_tokens=max_tokens,
                echo=False,       # don't repeat the prompt in output
                stop=["</s>"]     # stop at end-of-sequence
            )
            return result["choices"][0]["text"].strip()
        except Exception as e:
            print(f"❌ Phi-3 Mini prediction failed: {e}")
            raise


# Example usage:
# if __name__ == "__main__":
#     client = LLMClientPhi3()
#     while True:
#         user_input = input("Enter your prompt (or 'exit' to quit): ")
#         if user_input.lower() == 'exit':
#             break
#         response = client.get_response(user_input)
#         print("Phi-3 Mini Response:", response)
