import requests
import json
from typing import Optional

class LLMClientServer:
    """
    LLM client to interact with a running llama-server over HTTP.
    Mimics the interface of LLMClientGemma for easy integration.
    """
    def __init__(self, server_url: str = "http://localhost:8080", model_alias: str = "gemma-2b"):
        self.server_url = server_url.rstrip("/")
        self.model_alias = model_alias
        self.endpoint = f"{self.server_url}/v1/chat/completions"
        print(f"🔧 LLMClientServer initialized. Endpoint: {self.endpoint}, Model: {self.model_alias}")

    def get_response(self, prompt: str, max_tokens: int = 320, temperature: float = 0.2) -> str:
        """
        Sends a prompt to llama-server and returns the generated text.
        """
        payload = {
            "model": self.model_alias,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            # The generated text is in choices[0].message.content
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            print(f"❌ Request to LLaMA server failed: {e}")
            return "Error: Unable to get response from LLaMA server."

        except (KeyError, IndexError, TypeError) as e:
            print(f"❌ Unexpected response format from LLaMA server: {e}\nResponse: {response.text}")
            return "Error: Invalid response format from LLaMA server."


# # Example usage
# if __name__ == "__main__":
#     llm = LLMClientServer(server_url="http://localhost:8080", model_alias="gemma-2b")
#     prompt = "Explain Techmojo's leave policy in 3 sentences."
#     response = llm.get_response(prompt)
#     print("LLM Response:\n", response)
