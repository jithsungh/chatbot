from typing import Dict, Any

class Pipeline:
    def __init__(self):
        # Don't initialize components at startup - do it lazily
        self.router = None
        self.retriever = None
        self.history_manager = None
        self.promptGenerator = None
        self.llm_client = None
        self.response_formatter = None
        
        print("🔧 Pipeline created (components will be loaded lazily)")

    def _initialize_components(self):
        """Lazy initialization of components"""
        if self.router is not None:
            return  # Already initialized
            
        try:
            print("🔧 Initializing Pipeline components...")
            
            # Lazy imports to avoid circular dependencies
            from src.inference.HybridRouter import HybridDepartmentRouter
            from src.inference.ContextRetriever import SimpleContextRetriever
            from src.inference.HistoryManager import HistoryManager
            from src.inference.PromptGenerator import PromptGenerator
            from src.utils.LLMClientGemma import LLMClientGemma as LLMClient
            from src.utils.ResponseFormatter import ResponseFormatter
            
            self.router = HybridDepartmentRouter()
            print("✅ HybridDepartmentRouter initialized")
            
            self.retriever = SimpleContextRetriever()
            print("✅ SimpleContextRetriever initialized")
            
            self.history_manager = HistoryManager()
            print("✅ HistoryManager initialized")
            
            self.promptGenerator = PromptGenerator()
            print("✅ PromptGenerator initialized")
            
            self.llm_client = LLMClient()
            print("✅ LLMClient initialized")
            
            self.response_formatter = ResponseFormatter()
            print("✅ ResponseFormatter initialized")
            
            print("🎉 All Pipeline components initialized successfully!")
            
        except Exception as e:
            print(f"❌ Pipeline component initialization failed: {e}")
            raise

    def process_user_query(self, query: str, userid: str) -> Dict[str, Any]:
        try:
            # Initialize components only when first query comes in
            self._initialize_components()
            
            # 1) Determine department
            dept = self.router.route_query(query)

            # 2) Retrieve context
            chunks = self.retriever.retrieve_context(query=query, dept=dept, k=10, max_docs=5)
            context = " ,".join([c[0] for c in chunks])

            # 3) Get user history
            history = self.history_manager.get_context(userid, k=5)
            last_context = self.history_manager.get_last_context(userid)
            last_followup = self.history_manager.get_last_followup(userid)

            # 4) Generate prompt and get LLM response
            prompt = self.promptGenerator.generate_prompt(
                query=query, 
                context_text=context, 
                history_text=history, 
                last_context=last_context, 
                last_followup=last_followup
            )

            response = self.llm_client.get_response(prompt)
            parsed = self.response_formatter.to_json_object(response.content)

            # 5) Update history
            self.history_manager.update_context(
                userid, 
                question=query, 
                answer=parsed.answer, 
                followup=parsed.followup, 
                context=context
            )

            return parsed
        
        except Exception as e:
            print(f"❌ Error in pipeline processing: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your request. Please try again.",
                "followup": "Is there anything else I can help you with?",
                "error": str(e)
            }
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


