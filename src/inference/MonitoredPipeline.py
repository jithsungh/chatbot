"""
Monitored Pipeline - A drop-in replacement for your existing Pipeline.py

This version integrates the visualization system with minimal changes to your existing code.
Simply replace your Pipeline import with this MonitoredPipeline for instant visualization.

Usage:
    from src.inference.MonitoredPipeline import MonitoredPipeline as Pipeline
    # Use exactly like your original Pipeline
"""

from typing import Dict, Any
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from src.models import DeptFailure, UserQuestion
from src.config import Config
from src.utils.SecurityAnonymizer import get_anonymizer

# Import monitoring system
from interactive_pipeline_monitor import track_query, log_step, complete_step, error_step, finish_query, show_dashboard

class MonitoredPipeline:
    """
    Monitored version of your existing Pipeline with visualization capabilities.
    Drop-in replacement that adds comprehensive monitoring without changing the interface.
    """
    
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
        print("🔧 Monitored Pipeline created (components will be loaded lazily)")
        
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
        """Process user query with monitoring and visualization"""
        
        # 🔍 Start monitoring this query
        query_id = track_query(query, userid)
        
        try:
            # 1) Determine department
            step_idx = log_step(query_id, "Department Routing", {
                "query_length": len(query),
                "user_id": userid
            })
            
            try:
                dept = self.router.route_query(query)
                complete_step(query_id, step_idx, {
                    "detected_department": dept,
                    "routing_method": "hybrid"
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 2) Retrieve context
            step_idx = log_step(query_id, "Context Retrieval", {
                "department": dept,
                "k": 10
            })
            
            try:
                chunks = self.retriever.retrieve_context(query=query, dept=dept, k=10)
                context = " ,".join([c[0] for c in chunks])
                complete_step(query_id, step_idx, {
                    "chunks_found": len(chunks),
                    "total_context_length": len(context)
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 3) Get user history
            step_idx = log_step(query_id, "History Management", {
                "user_id": userid
            })
            
            try:
                history = await self.history_manager.get_context(userid, k=5)
                last_context = await self.history_manager.get_last_context(userid)
                last_followup = await self.history_manager.get_last_followup(userid)
                
                complete_step(query_id, step_idx, {
                    "history_length": len(history) if history else 0,
                    "has_last_context": bool(last_context),
                    "has_last_followup": bool(last_followup)
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 4) Generate prompt and get LLM response
            step_idx = log_step(query_id, "Prompt Generation", {
                "department": dept,
                "context_provided": bool(context),
                "history_provided": bool(history)
            })
            
            try:
                prompt = await self.promptGenerator.generate_prompt(
                    query=query, 
                    dept=dept,
                    context_text=context, 
                    history_text=history, 
                    last_context=last_context, 
                    last_followup=last_followup
                )
                
                complete_step(query_id, step_idx, {
                    "prompt_length": len(prompt),
                    "prompt_word_count": len(prompt.split())
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 5) Security - Anonymize prompt
            step_idx = log_step(query_id, "Security Anonymization", {
                "original_prompt_length": len(prompt)
            })
            
            try:
                # 🔒 Anonymize prompt before sending to LLM for security
                anonymized_prompt = self.anonymizer.anonymize_prompt(prompt)
                
                complete_step(query_id, step_idx, {
                    "anonymized_prompt_length": len(anonymized_prompt),
                    "anonymization_applied": len(anonymized_prompt) != len(prompt)
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 6) LLM Processing
            step_idx = log_step(query_id, "LLM Processing", {
                "input_length": len(anonymized_prompt)
            })
            
            try:
                # Send anonymized prompt to LLM
                response = self.llm_client.get_response(anonymized_prompt)
                
                complete_step(query_id, step_idx, {
                    "response_length": len(response),
                    "estimated_tokens": len(response.split())
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 7) Security - Deanonymize response
            step_idx = log_step(query_id, "Security Deanonymization", {
                "original_response_length": len(response)
            })
            
            try:
                # 🔓 Deanonymize response to restore original organization names
                deanonymized_response = self.anonymizer.deanonymize_response(response)
                
                complete_step(query_id, step_idx, {
                    "deanonymized_response_length": len(deanonymized_response),
                    "deanonymization_applied": len(deanonymized_response) != len(response)
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 8) Format response
            step_idx = log_step(query_id, "Response Formatting", {
                "raw_response_length": len(deanonymized_response)
            })
            
            try:
                parsed = self.response_formatter.to_json_object(deanonymized_response)
                
                complete_step(query_id, step_idx, {
                    "parsing_successful": True,
                    "answer_length": len(parsed.answer) if hasattr(parsed, 'answer') else 0,
                    "has_followup": hasattr(parsed, 'followup') and bool(parsed.followup)
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                raise
            
            # 9) Update history (keep this synchronous as it's needed for conversation flow)
            step_idx = log_step(query_id, "History Update", {
                "user_id": userid
            })
            
            try:
                await self.history_manager.update_context(
                    userid, 
                    question=query, 
                    answer=parsed.answer, 
                    followup=parsed.followup, 
                    context=context
                )
                
                complete_step(query_id, step_idx, {
                    "history_updated": True
                })
            except Exception as e:
                error_step(query_id, step_idx, str(e))
                # Don't raise here as this is not critical
            
            # 10) Submit async database operations (non-blocking)
            if hasattr(parsed, 'org_related') and parsed.org_related:
                self._submit_async_db_operations(dept, parsed, userid, context)
            
            # 🏁 Finish monitoring
            finish_query(query_id, parsed)
            
            return parsed
            
        except Exception as e:
            print(f"❌ Error in pipeline processing: {e}")
            
            # Still finish the query tracking on error
            finish_query(query_id)
            
            return {
                "answer": "I apologize, but I encountered an error processing your request. Please try again.",
                "followup": "Is there anything else I can help you with?",
                "error": str(e)
            }
    
    def show_monitoring_dashboard(self):
        """Display the live monitoring dashboard"""
        show_dashboard()
    
    def __del__(self):
        """Cleanup thread pool on destruction"""
        try:
            if hasattr(self, 'db_executor'):
                self.db_executor.shutdown(wait=True)
        except:
            pass

# For easy testing
async def main():
    """Test the monitored pipeline"""
    pipeline = MonitoredPipeline()
    user_id = "test_user"
    
    print("==============================================")
    print("    Welcome to Monitored Pipeline Demo      ")
    print("==============================================\n")
    
    # Process a few test queries
    test_queries = [
        "What is the company policy on sick leave?",
        "My computer is running slowly, can you help?",
        "What are the office hours?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Processing Query {i}/{len(test_queries)} ---")
        
        start = time.time()
        result = await pipeline.process_user_query(query, f"{user_id}_{i}")
        end = time.time()
        
        print(f"AI Response: {result.answer[:100]}...")
        print(f"Time taken: {end - start:.2f} seconds")
        
        # Show dashboard after each query
        if i == len(test_queries):
            print("\n--- Final Dashboard ---")
            pipeline.show_monitoring_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
