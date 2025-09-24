from types import SimpleNamespace
import json

class ResponseFormatter:
    @staticmethod
    def to_json_object(response_content: str) -> SimpleNamespace:
        try:
            # if response_content starts with ```,remove them
            if response_content.startswith("```") and response_content.endswith("```"):
                response_content = response_content[3:-3].strip()
            
            if response_content.startswith("json"):
                response_content = response_content[4:].strip()

            return json.loads(response_content, object_hook=lambda d: SimpleNamespace(**d))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}\nRaw content: {response_content}")


    @staticmethod
    def pretty_print(data) -> None:
        """
        Nicely print a SimpleNamespace or dict as JSON.
        Recursively converts SimpleNamespace to dict if needed.
        """
        def to_dict(obj):
            if isinstance(obj, SimpleNamespace):
                return {k: to_dict(v) for k, v in vars(obj).items()}
            elif isinstance(obj, list):
                return [to_dict(i) for i in obj]
            else:
                return obj

        print(json.dumps(to_dict(data), indent=4, ensure_ascii=False))


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
