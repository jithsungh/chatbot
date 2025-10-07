from typing import Dict, Any
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from src.models import DeptFailure, UserQuestion
from src.config import Config
from src.utils.SecurityAnonymizer import get_anonymizer
from src.inference.PipelineVisualizer import visualizer, Colors

class EnhancedPipeline:
    """
    Enhanced Pipeline with comprehensive visualization and monitoring.
    Every step is tracked, timed, and beautifully displayed.
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
        
        # Print initialization
        visualizer.print_header()
        print(f"{Colors.OKCYAN}🔧 Enhanced Pipeline created (components will be loaded lazily){Colors.ENDC}")
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Lazy initialization of components with visualization"""
        if self.router is not None:
            return  # Already initialized
        
        with visualizer.step("Component Initialization", Colors.OKBLUE):
            try:
                print(f"{Colors.OKBLUE}🔧 Initializing Pipeline components...{Colors.ENDC}")
                
                # Lazy imports to avoid circular dependencies
                from src.inference.EnhancedRouter import EnhancedDepartmentRouter
                from src.inference.EnhancedRetriever import EnhancedContextRetriever
                from src.inference.EnhancedPromptGenerator import EnhancedPromptGenerator
                from src.utils.EnhancedLLMClient import EnhancedLLMClient
                from src.utils.EnhancedResponseFormatter import EnhancedResponseFormatter
                from src.config import Config
                
                # Initialize with sub-steps
                with visualizer.step("Router Initialization", Colors.ROUTER):
                    self.router = EnhancedDepartmentRouter()
                    visualizer.add_data("router_type", "EnhancedDepartmentRouter")
                    
                with visualizer.step("Context Retriever Initialization", Colors.RETRIEVER):
                    self.retriever = EnhancedContextRetriever()
                    visualizer.add_data("retriever_type", "EnhancedContextRetriever")
                    
                with visualizer.step("History Manager Initialization", Colors.HISTORY):
                    self.history_manager = Config.HISTORY_MANAGER
                    visualizer.add_data("history_manager_type", type(self.history_manager).__name__)
                    
                with visualizer.step("Prompt Generator Initialization", Colors.PROMPT):
                    self.promptGenerator = EnhancedPromptGenerator()
                    visualizer.add_data("prompt_generator_type", "EnhancedPromptGenerator")
                    
                with visualizer.step("LLM Client Initialization", Colors.LLM):
                    self.llm_client = EnhancedLLMClient()
                    visualizer.add_data("llm_client_type", "EnhancedLLMClient")
                    
                with visualizer.step("Response Formatter Initialization", Colors.FORMATTER):
                    self.response_formatter = EnhancedResponseFormatter()
                    visualizer.add_data("formatter_type", "EnhancedResponseFormatter")
                
                visualizer.add_data("components_initialized", 6)
                print(f"{Colors.OKGREEN}🎉 All Pipeline components initialized successfully!{Colors.ENDC}")
                
            except Exception as e:
                print(f"{Colors.FAIL}❌ Pipeline component initialization failed: {e}{Colors.ENDC}")
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
                    print(f"{Colors.WARNING}📝 Department failure logged: {dept} -> {parsed_dept}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.FAIL}❌ Error logging department failure: {e}{Colors.ENDC}")
                finally:
                    session.close()
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error in async dept failure check: {e}{Colors.ENDC}")
    
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
                print(f"{Colors.OKCYAN}📝 User question saved for analysis: {std_question[:50]}...{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}❌ Error saving user question: {e}{Colors.ENDC}")
                session.rollback()
            finally:
                session.close()
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error in async user question save: {e}{Colors.ENDC}")
    
    def _submit_async_db_operations(self, dept: str, parsed, userid: str, context: str):
        """Submit database operations to thread pool for async execution"""
        try:
            with visualizer.step("Database Operations Submission", Colors.WARNING):
                # Submit department failure check
                if dept != parsed.dept and len(parsed.std_question) > 20:
                    self.db_executor.submit(
                        self._async_dept_failure_check, 
                        dept, 
                        parsed.dept, 
                        parsed.std_question
                    )
                    visualizer.add_data("dept_failure_logged", True)
                
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
                    visualizer.add_data("user_question_saved", True)
                    
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error submitting async database operations: {e}{Colors.ENDC}")
    
    async def process_user_query(self, query: str, userid: str) -> Dict[str, Any]:
        """Process user query with comprehensive visualization"""
        
        # Print query header
        visualizer.print_query_header(query, userid)
        total_start_time = time.perf_counter()
        
        try:
            # 1) Determine department
            with visualizer.step("Department Routing", Colors.ROUTER) as step:
                dept = self.router.route_query_with_details(query)
                step_data = {
                    'detected_department': dept['department'],
                    'routing_method': dept['method'],
                    'confidence': dept['confidence'],
                    'keyword_matches': dept.get('keyword_matches', []),
                    'embedding_similarity': dept.get('embedding_similarity', {})
                }
                visualizer.add_data("routing_result", step_data)
                visualizer.print_routing_analysis(query, dept['department'], step_data)
            
            department = dept['department']
            
            # 2) Retrieve context
            with visualizer.step("Context Retrieval", Colors.RETRIEVER) as step:
                chunks = self.retriever.retrieve_context_with_details(query=query, dept=department, k=10)
                context = " ,".join([c[0] for c in chunks['chunks']])
                
                context_data = {
                    'chunks_found': len(chunks['chunks']),
                    'total_length': len(context),
                    'filter_applied': chunks['filter_applied'],
                    'search_time': chunks['search_time'],
                    'model_used': chunks['model_used']
                }
                visualizer.add_data("context_data", context_data)
                visualizer.print_context_analysis(chunks['chunks'], context_data)
            
            # 3) Get user history
            with visualizer.step("History Management", Colors.HISTORY) as step:
                history = await self.history_manager.get_context(userid, k=5)
                last_context = await self.history_manager.get_last_context(userid)
                last_followup = await self.history_manager.get_last_followup(userid)
                
                history_data = {
                    'history_items': history.split('\n') if history else [],
                    'last_context': last_context,
                    'last_followup': last_followup,
                    'history_length': len(history) if history else 0
                }
                visualizer.add_data("history_data", history_data)
                visualizer.print_history_analysis(history_data)
            
            # 4) Generate prompt
            with visualizer.step("Prompt Generation", Colors.PROMPT) as step:
                prompt_result = await self.promptGenerator.generate_prompt_with_details(
                    query=query, 
                    dept=department,
                    context_text=context, 
                    history_text=history, 
                    last_context=last_context, 
                    last_followup=last_followup
                )
                
                prompt = prompt_result['prompt']
                prompt_data = {
                    'prompt_length': len(prompt),
                    'template_used': prompt_result['template_used'],
                    'components': prompt_result['components']
                }
                visualizer.add_data("prompt_data", prompt_data)
                visualizer.print_prompt_analysis(prompt_data)
            
            # 5) Security - Anonymize prompt
            with visualizer.step("Security Anonymization", Colors.SECURITY) as step:
                anonymized_prompt = self.anonymizer.anonymize_prompt(prompt)
                
                security_data = {
                    'prompt_sanitized': len(anonymized_prompt) != len(prompt),
                    'original_length': len(prompt),
                    'anonymized_length': len(anonymized_prompt)
                }
                
                # Get anonymization details if available
                if hasattr(self.anonymizer, 'get_last_anonymizations'):
                    security_data['anonymizations'] = self.anonymizer.get_last_anonymizations()
                
                visualizer.add_data("security_data", security_data)
                visualizer.print_security_analysis(security_data)
            
            # 6) LLM Response
            with visualizer.step("LLM Processing", Colors.LLM) as step:
                llm_result = self.llm_client.get_response_with_details(anonymized_prompt)
                response = llm_result['response']
                
                llm_data = {
                    'model_name': llm_result.get('model_name', 'Unknown'),
                    'response_time': llm_result.get('response_time', 0),
                    'input_tokens': llm_result.get('input_tokens', len(anonymized_prompt.split())),
                    'output_tokens': llm_result.get('output_tokens', len(response.split())),
                    'raw_response_length': len(response)
                }
                visualizer.add_data("llm_data", llm_data)
                visualizer.print_llm_analysis(llm_data)
            
            # 7) Security - Deanonymize response
            with visualizer.step("Security Deanonymization", Colors.SECURITY) as step:
                deanonymized_response = self.anonymizer.deanonymize_response(response)
                
                security_data = {
                    'response_deanonymized': len(deanonymized_response) != len(response),
                    'original_length': len(response),
                    'deanonymized_length': len(deanonymized_response)
                }
                visualizer.add_data("deanonymize_data", security_data)
            
            # 8) Format response
            with visualizer.step("Response Formatting", Colors.FORMATTER) as step:
                format_result = self.response_formatter.to_json_object_with_details(deanonymized_response)
                parsed = format_result['parsed']
                
                format_data = {
                    'parsing_method': format_result.get('parsing_method', 'standard'),
                    'json_extracted': format_result.get('json_extracted', True),
                    'fields_found': format_result.get('fields_found', []),
                    'answer_length': len(parsed.answer) if hasattr(parsed, 'answer') else 0,
                    'followup_generated': hasattr(parsed, 'followup') and bool(parsed.followup)
                }
                visualizer.add_data("format_data", format_data)
                visualizer.print_formatting_analysis(format_data)
            
            # 9) Update history
            with visualizer.step("History Update", Colors.HISTORY) as step:
                await self.history_manager.update_context(
                    userid, 
                    question=query, 
                    answer=parsed.answer, 
                    followup=parsed.followup, 
                    context=context
                )
                visualizer.add_data("history_updated", True)
            
            # 10) Submit async database operations (if needed)
            if hasattr(parsed, 'org_related') and parsed.org_related:
                self._submit_async_db_operations(department, parsed, userid, context)
            
            # Calculate total time and print summary
            total_end_time = time.perf_counter()
            total_time = total_end_time - total_start_time
            
            visualizer.print_final_summary(total_time, parsed)
            
            return parsed
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error in pipeline processing: {e}{Colors.ENDC}")
            
            # Create error result as SimpleNamespace for consistency
            from types import SimpleNamespace
            error_result = SimpleNamespace()
            error_result.answer = "I apologize, but I encountered an error processing your request. Please try again."
            error_result.followup = "Is there anything else I can help you with?"
            error_result.error = str(e)
            error_result.org_related = False
            
            return error_result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return visualizer.get_session_stats()
    
    def clear_session(self):
        """Clear visualization session data"""
        visualizer.clear_session()
    
    def __del__(self):
        """Cleanup thread pool on destruction"""
        try:
            if hasattr(self, 'db_executor'):
                self.db_executor.shutdown(wait=True)
        except:
            pass
