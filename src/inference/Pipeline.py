from typing import Dict, Any
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from src.models import DeptFailure, UserQuestion
from src.config import Config
from src.utils.SecurityAnonymizer import get_anonymizer

class Pipeline:
    def __init__(self):
        # Don't initialize components at startup - do it lazily
        self.router = None
        self.retriever = None
        self.history_manager = None
        self.promptGenerator = None
        self.llm_client = None
        self.response_formatter = None
          # Thread pool for async database operations
        self.db_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="db_ops")
        
        # Initialize security anonymizer
        self.anonymizer = get_anonymizer()
        print("🔧 Pipeline created (components will be loaded lazily)")

        # Initialize components
        self._initialize_components()
        

    def _initialize_components(self):
        """Lazy initialization of components"""
        if self.router is not None:
            return  # Already initialized
            
        try:
            print("🔧 Initializing Pipeline components...")
            
            # Lazy imports to avoid circular dependencies
            from src.inference.HybridRouter import HybridDepartmentRouter
            from src.inference.ContextRetriever import SimpleContextRetriever
            from src.inference.PromptGenerator import PromptGenerator
            from src.utils.LLMClientServer import LLMClientServer as LLMClient
            from src.utils.ResponseFormatter import ResponseFormatter
            from src.config import Config
            
            self.router = HybridDepartmentRouter()
            print("✅ HybridDepartmentRouter initialized")
            
            self.retriever = SimpleContextRetriever()
            print("✅ SimpleContextRetriever initialized")
            
            self.history_manager = Config.HISTORY_MANAGER
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

    def _async_dept_failure_check(self, dept: str, parsed_dept: str, std_question: str):
        """Async function to handle department failure logging"""
        try:
            if dept != parsed_dept:
                session = Config.get_session()
                try:
                    DeptFailure.create(
                        session,
                        query=std_question,
                        detected=dept,
                        expected=parsed_dept,
                    )
                    print(f"📝 Department failure logged: {dept} -> {parsed_dept}")
                except Exception as e:
                    print(f"❌ Error logging department failure: {e}")
                finally:
                    session.close()
        except Exception as e:
            print(f"❌ Error in async dept failure check: {e}")

    def _async_user_question_save(self, userid: str, std_question: str, answer: str, context: str, dept: str):
        """Async function to handle user question saving"""
        try:
            session = Config.get_session()
            try:
                new_record = UserQuestion(
                    userid=userid,
                    query=std_question,
                    answer=answer,
                    context=context,
                    dept=dept,
                    source='context'
                )
                session.add(new_record)
                session.commit()
                print(f"📝 User question saved for analysis: {std_question[:50]}...")
            except Exception as e:
                print(f"❌ Error saving user question: {e}")
                session.rollback()
            finally:
                session.close()
        except Exception as e:
            print(f"❌ Error in async user question save: {e}")

    def _submit_async_db_operations(self, dept: str, parsed, userid: str, context: str):
        """Submit database operations to thread pool for async execution"""
        try:
            # Submit department failure check
            if dept != parsed.dept and len(parsed.std_question) > 20:
                self.db_executor.submit(
                    self._async_dept_failure_check, 
                    dept, 
                    parsed.dept, 
                    parsed.std_question
                )
            
            # Submit user question save for context-less queries
            if not parsed.has_context and len(parsed.std_question) > 20:
                self.db_executor.submit(
                    self._async_user_question_save,
                    userid,
                    parsed.std_question,
                    parsed.answer,
                    context,
                    parsed.dept
                )
                
        except Exception as e:
            print(f"❌ Error submitting async database operations: {e}")

    async def process_user_query(self, query: str, userid: str) -> Dict[str, Any]:
        try:
            # 1) Determine department
            dept = self.router.route_query(query)

            # 2) Retrieve context
            chunks = self.retriever.retrieve_context(query=query, dept=dept, k=10)
            context = " ,".join([c[0] for c in chunks])

            # 3) Get user history
            history = await self.history_manager.get_context(userid, k=5)
            last_context = await self.history_manager.get_last_context(userid)
            last_followup = await self.history_manager.get_last_followup(userid)            # 4) Generate prompt and get LLM response
            prompt = await self.promptGenerator.generate_prompt(
                query=query, 
                dept=dept,
                context_text=context, 
                history_text=history, 
                last_context=last_context, 
                last_followup=last_followup
            )

            # 🔒 Anonymize prompt before sending to LLM for security
            anonymized_prompt = self.anonymizer.anonymize_prompt(prompt)
            # print(f"📝 Generated Prompt:\n{anonymized_prompt}\n")

            # Send anonymized prompt to LLM
            response = self.llm_client.get_response(anonymized_prompt)
            
            # 🔓 Deanonymize response to restore original organization names
            deanonymized_response = self.anonymizer.deanonymize_response(response)
            # print(f"💬 LLM Response: {deanonymized_response}")
            # print("\n\n response type:", type(deanonymized_response), "\n\n")
            parsed = self.response_formatter.to_json_object(deanonymized_response)

            # 5) Update history (keep this synchronous as it's needed for conversation flow)
            await self.history_manager.update_context(
                userid, 
                question=query, 
                answer=parsed.answer, 
                followup=parsed.followup, 
                context=context
            )
            # Return response immediately without waiting for DB operations
            return parsed

            # 6) Submit async database operations (non-blocking)
            if parsed.org_related:
                self._submit_async_db_operations(dept, parsed, userid, context)
                
        
        except Exception as e:
            print(f"❌ Error in pipeline processing: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your request. Please try again.",
                "followup": "Is there anything else I can help you with?",
                "error": str(e)
            }

    def __del__(self):
        """Cleanup thread pool on destruction"""
        try:
            if hasattr(self, 'db_executor'):
                self.db_executor.shutdown(wait=True)
        except:
            pass
        
async def main():
    pipeline = Pipeline()
    user_id = "user123"

    print("==============================================")
    print("       Welcome to Techmojo AI Assistant       ")
    print("Type your message and press Enter to chat.")
    print("Type 'exit' or 'quit' to leave the chat.")
    print("==============================================\n")

    while True:
        try:
            user_query = input("You: ").strip()
            if user_query.lower() in {"exit", "quit"}:
                print("\nGoodbye! 👋")
                break

            # Measure LLM response time
            start = time.time()
            result = await pipeline.process_user_query(user_query, user_id)
            end = time.time()

            # print("\n------------------ AI Response ------------------")
            # ResponseFormatter.pretty_print(result)
            # print(f"\n⏱ Time taken: {end - start:.2f} seconds")
            # print("-------------------------------------------------\n")
            print("AI: ", result.answer)
            print("\n    ",result.followup)
            print(f"\n    ⏱ Time taken: {end - start:.2f} seconds\n")

            print("==============================================\n")
            print(result)
            print("==============================================\n")

        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error processing your query: {e}\n")

# if __name__ == "__main__":
#     asyncio.run(main())


