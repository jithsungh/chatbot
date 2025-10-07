from types import SimpleNamespace
import json
import re

class ResponseFormatter:
    """
    A robust JSON response parser and formatter for LLM outputs.
    Safely extracts JSON from noisy or markdown-wrapped text and returns it as an easy-to-access object.
    """

    @staticmethod
    def to_json_object(response_content: str) -> SimpleNamespace:
        """
        Convert an LLM text response into a structured SimpleNamespace object.
        Gracefully handles:
          - ```json ... ``` fenced code blocks
          - Extra markdown or text before/after JSON
          - Trailing commas or minor formatting inconsistencies
        """
        try:
            if not response_content or not isinstance(response_content, str):
                raise ValueError("Empty or invalid response content received.")

            # 🧹 Clean markdown fences
            response_content = response_content.strip()
            response_content = re.sub(r"^```(json)?|```$", "", response_content, flags=re.IGNORECASE).strip()

            # 🧠 Extract JSON block (first valid {...})
            match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON object found in response: {response_content[:200]}...")

            json_str = match.group().strip()

            # 🧰 Optional: remove trailing commas
            json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

            # ✅ Parse JSON safely
            parsed = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))
            return parsed

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}\nRaw content:\n{response_content}")
        except Exception as e:
            raise ValueError(f"Error parsing LLM response: {e}\nRaw content:\n{response_content}")

    @staticmethod
    def to_dict(obj):
        """Recursively convert SimpleNamespace or nested objects to dict."""
        if isinstance(obj, SimpleNamespace):
            return {k: ResponseFormatter.to_dict(v) for k, v in vars(obj).items()}
        elif isinstance(obj, list):
            return [ResponseFormatter.to_dict(i) for i in obj]
        else:
            return obj

    @staticmethod
    def pretty_print(data) -> None:
        """Nicely format and print JSON output with proper indentation."""
        try:
            print(json.dumps(ResponseFormatter.to_dict(data), indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"⚠️ Failed to pretty print data: {e}")



# # Example usage:
# if __name__ == "__main__":
#     raw_response = '''{
#     "org_related": true,
#     "has_context": true,
#     "answer": "Techmojo Solutions Pvt Ltd is a technology company specializing in AI and cloud solutions.",
#     "followup": "What specific aspect of Techmojo would you like to know more about?",
#     "std_question": "What is Techmojo Solutions Pvt Ltd?"
#     }
#     '''

#     try:
#         parsed = ResponseFormatter.to_json_object(raw_response)
#         # parsed = vars(parsed)
#         ResponseFormatter.pretty_print(parsed)
#         print("Type of parsed response:", type(parsed))
#         print("org_related:", parsed.org_related, "Type:", type(parsed.org_related))
#         print("has_context:", parsed.has_context, "Type:", type(parsed.has_context))
#         print("answer:", parsed.answer, "Type:", type(parsed.answer))
#         print("followup:", parsed.followup, "Type:", type(parsed.followup))
#         print("std_question:", parsed.std_question, "Type:", type(parsed.std_question))
        
#     except ValueError as e:
#         print(e)
