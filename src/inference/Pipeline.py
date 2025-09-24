import time

from src.inference.HybridRouter import HybridDepartmentRouter
from src.inference.ContextRetriever import SimpleContextRetriever
from src.inference.HistoryManager import HistoryManager
from src.inference.PromptGenerator import PromptGenerator
# from src.inference.LLMClientGoogle import LLMClientGoogle as LLMClient
# from src.inference.LLMClientOpenAI import LLMClientOpenAI as LLMClient
# from src.inference.LLMClient import LLMClient
from src.inference.LLMClientGemma import LLMClientGemma as LLMClient
from src.inference.ResponseFormatter import ResponseFormatter


class Pipeline:

    def __init__(self):
        self.router = HybridDepartmentRouter()
        self.retriever = SimpleContextRetriever()
        self.history_manager = HistoryManager(max_turns=10)
        self.promptGenerator = PromptGenerator()
        self.llm_client = LLMClient()
        self.response_formatter = ResponseFormatter()

    def process_user_query(self, query: str,userid) -> dict:


        ## 1) determine department
        dept = self.router.route_query(query)

        ## 2) retrieve context
        chunks = self.retriever.retrieve_context(query=query, dept=dept, k=10, max_docs=5)
        context = " ,".join([c[0] for c in chunks])

        ## 3) get user history
        history = self.history_manager.get_context(userid, k=5)  # get last 10 turns
        last_context = self.history_manager.get_last_context(userid)
        last_followup = self.history_manager.get_last_followup(userid)

        ## 4) invoke LLM with context and get response
        # generate prompt
        prompt = self.promptGenerator.generate_prompt(query=query, context_text=context, history_text=history, last_context=last_context, last_followup=last_followup)

        # get response
        response = self.llm_client.get_response(prompt)

        # parse response
        parsed = self.response_formatter.to_json_object(response.content)

        ## 5) update history
        self.history_manager.update_context(userid, question=query, answer=parsed.answer, followup=parsed.followup, context=context)

        return parsed
    
# if __name__ == "__main__":
#     pipeline = Pipeline()
#     user_id = "user123"

#     print("==============================================")
#     print("       Welcome to Techmojo AI Assistant       ")
#     print("Type your message and press Enter to chat.")
#     print("Type 'exit' or 'quit' to leave the chat.")
#     print("==============================================\n")

#     while True:
#         try:
#             user_query = input("You: ").strip()
#             if user_query.lower() in {"exit", "quit"}:
#                 print("\nGoodbye! 👋")
#                 break

#             # Measure LLM response time
#             start = time.time()
#             result = pipeline.process_user_query(user_query, user_id)
#             end = time.time()

#             # print("\n------------------ AI Response ------------------")
#             # ResponseFormatter.pretty_print(result)
#             # print(f"\n⏱ Time taken: {end - start:.2f} seconds")
#             # print("-------------------------------------------------\n")
#             print("AI: ", result.answer)
#             print("\n    ",result.followup)
#             print(f"\n    ⏱ Time taken: {end - start:.2f} seconds\n")

#         except KeyboardInterrupt:
#             print("\nInterrupted by user. Exiting...")
#             break
#         except Exception as e:
#             print(f"\n❌ Error processing your query: {e}\n")


