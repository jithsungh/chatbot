from llama_cpp import Llama, LlamaGrammar


class LLMClientLlama:
    def __init__(self):
        print("LLaMA client init")
        """Initialize LLaMA LLM"""
        try:
            # Load once (big init cost, so keep this global/singleton)
            self.llm = Llama(
                model_path="/home/jithsungh/llama_models/llama-3.2-3b-instruct-q4_k_m.gguf",
                n_threads=32,
                n_ctx=4096,
                verbose=False
            )
            print("✅ LLaMA model loaded")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            raise

        self.grammar = LlamaGrammar.from_string(r"""
            root ::= object
            object ::= "{" members "}"
            members ::= pair ("," pair)*
            pair ::= string ":" value
            string ::= "\"" ([^"\\] | "\\" .)* "\""
            value ::= string | "true" | "false" | object
            """)

    def get_response(self, prompt: str, max_tokens: int = 256) -> str:
        """Get response from LLaMA LLM"""
        try:
            result = self.llm(
                prompt,
                grammar=self.grammar,
                max_tokens=max_tokens,
                echo=False,        # don't repeat the prompt in output
                stop=["</s>"]      # stop at end-of-sequence
            )
            return result["choices"][0]["text"].strip()
        except Exception as e:
            print(f"❌ LLM prediction failed: {e}")
            raise


# Example
# if __name__ == "__main__":
#     client = LLMClientLlama()
    
#     while True:
#         user_input = input("Enter your prompt (or 'exit' to quit): ")
#         if user_input.lower() == 'exit':
#             break
#         response = client.get_response(user_input)
#         print("LLaMA Response:", response)
