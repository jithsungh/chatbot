from llama_cpp import Llama

# Load once (big init cost, so keep this global/singleton)
llm = Llama(
    model_path="/home/jithsungh/llama_models/llama-3.2-3b-instruct-q4_k_m.gguf",
    n_threads=32,
    n_ctx=2048,
    verbose=False
)

def query_llm(prompt: str, max_tokens: int = 256) -> str:
    """Send a stateless prompt to LLaMA and return raw text output."""
    result = llm(
        prompt,
        max_tokens=max_tokens,
        echo=False,        # don't repeat the prompt in output
        stop=["</s>"]      # stop at end-of-sequence
    )
    return result["choices"][0]["text"].strip()

# Example
if __name__ == "__main__":
    
    while True:
        user_input = input("Enter your prompt (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        response = query_llm(user_input)
        print("LLaMA Response:", response)
