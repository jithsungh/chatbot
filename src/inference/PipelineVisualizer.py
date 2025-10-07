import time
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import contextmanager

# Color codes for beautiful console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Additional colors for different components
    ROUTER = '\033[35m'      # Magenta
    RETRIEVER = '\033[36m'   # Cyan  
    HISTORY = '\033[33m'     # Yellow
    PROMPT = '\033[32m'      # Green
    LLM = '\033[31m'         # Red
    FORMATTER = '\033[34m'   # Blue
    SECURITY = '\033[37m'    # White

@dataclass
class StepInfo:
    name: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    status: str = "pending"  # pending, running, success, error
    data: Dict[str, Any] = field(default_factory=dict)
    sub_steps: List['StepInfo'] = field(default_factory=list)
    error: Optional[str] = None

class PipelineVisualizer:
    """
    Comprehensive visualization tool for the inference pipeline.
    Tracks every step, timing, and data flow with beautiful console output.
    """
    
    def __init__(self):
        self.steps: List[StepInfo] = []
        self.current_step: Optional[StepInfo] = None
        self.session_start_time = time.perf_counter()
        self.total_queries = 0
        
    def print_header(self):
        """Print beautiful header for the pipeline visualization"""
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🚀 INFERENCE PIPELINE VISUALIZATION 🚀{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Total Queries Processed: {self.total_queries}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    def print_query_header(self, query: str, userid: str):
        """Print query information"""
        self.total_queries += 1
        print(f"\n{Colors.BOLD}📝 QUERY #{self.total_queries}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}User ID: {userid}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Query: {Colors.BOLD}{query[:100]}{'...' if len(query) > 100 else ''}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Timestamp: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{'-'*60}{Colors.ENDC}\n")
    
    @contextmanager
    def step(self, name: str, color: str = Colors.OKGREEN):
        """Context manager for tracking pipeline steps"""
        step_info = StepInfo(name=name)
        step_info.start_time = time.perf_counter()
        step_info.status = "running"
        
        self.steps.append(step_info)
        self.current_step = step_info
        
        # Print step start
        print(f"{color}🔄 {name}...{Colors.ENDC}")
        
        try:
            yield step_info
            step_info.status = "success"
            step_info.end_time = time.perf_counter()
            step_info.duration = step_info.end_time - step_info.start_time
            
            # Print step completion
            print(f"{Colors.OKGREEN}✅ {name} completed in {step_info.duration:.3f}s{Colors.ENDC}")
            
        except Exception as e:
            step_info.status = "error"
            step_info.error = str(e)
            step_info.end_time = time.perf_counter()
            step_info.duration = step_info.end_time - step_info.start_time
            
            print(f"{Colors.FAIL}❌ {name} failed after {step_info.duration:.3f}s: {e}{Colors.ENDC}")
            raise
        finally:
            self.current_step = None
    
    def add_data(self, key: str, value: Any):
        """Add data to the current step"""
        if self.current_step:
            self.current_step.data[key] = value
    
    def print_step_details(self, step_name: str, details: Dict[str, Any], color: str = Colors.OKCYAN):
        """Print detailed information for a step"""
        print(f"{color}📊 {step_name} Details:{Colors.ENDC}")
        for key, value in details.items():
            if isinstance(value, (dict, list)):
                print(f"{color}   {key}: {json.dumps(value, indent=2)}{Colors.ENDC}")
            elif isinstance(value, str) and len(value) > 100:
                print(f"{color}   {key}: {value[:100]}...{Colors.ENDC}")
            else:
                print(f"{color}   {key}: {value}{Colors.ENDC}")
        print()
    
    def print_routing_analysis(self, query: str, dept: str, router_data: Dict[str, Any]):
        """Print detailed routing analysis"""
        print(f"{Colors.ROUTER}🎯 DEPARTMENT ROUTING ANALYSIS{Colors.ENDC}")
        print(f"{Colors.ROUTER}Query (cleaned): {router_data.get('cleaned_query', query.lower())}{Colors.ENDC}")
        print(f"{Colors.ROUTER}Detected Department: {Colors.BOLD}{dept}{Colors.ENDC}")
        
        if 'keyword_matches' in router_data:
            print(f"{Colors.ROUTER}Keyword Matches: {router_data['keyword_matches']}{Colors.ENDC}")
        
        if 'embedding_similarity' in router_data:
            print(f"{Colors.ROUTER}Embedding Similarities: {router_data['embedding_similarity']}{Colors.ENDC}")
        
        if 'routing_method' in router_data:
            print(f"{Colors.ROUTER}Routing Method: {router_data['routing_method']}{Colors.ENDC}")
        
        print()
    
    def print_context_analysis(self, chunks: List[tuple], context_data: Dict[str, Any]):
        """Print context retrieval analysis"""
        print(f"{Colors.RETRIEVER}🔍 CONTEXT RETRIEVAL ANALYSIS{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Retrieved Chunks: {len(chunks)}{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Total Context Length: {context_data.get('total_length', 0)} chars{Colors.ENDC}")
        
        if 'filter_applied' in context_data:
            print(f"{Colors.RETRIEVER}Department Filter: {context_data['filter_applied']}{Colors.ENDC}")
        
        if chunks:
            print(f"{Colors.RETRIEVER}Top Chunks Preview:{Colors.ENDC}")
            for i, (chunk, score) in enumerate(chunks[:3]):
                preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                print(f"{Colors.RETRIEVER}   {i+1}. Score: {score:.3f} | {preview}{Colors.ENDC}")
        print()
    
    def print_history_analysis(self, history_data: Dict[str, Any]):
        """Print history management analysis"""
        print(f"{Colors.HISTORY}📚 HISTORY MANAGEMENT ANALYSIS{Colors.ENDC}")
        
        for key, value in history_data.items():
            if key == 'history_items' and isinstance(value, list):
                print(f"{Colors.HISTORY}Previous Conversations: {len(value)} items{Colors.ENDC}")
                for i, item in enumerate(value[-3:]):  # Show last 3
                    print(f"{Colors.HISTORY}   {i+1}. {item[:80]}...{Colors.ENDC}")
            elif key == 'last_context' and value:
                print(f"{Colors.HISTORY}Last Context: {value[:80]}...{Colors.ENDC}")
            elif key == 'last_followup' and value:
                print(f"{Colors.HISTORY}Last Followup: {value[:80]}...{Colors.ENDC}")
            else:
                print(f"{Colors.HISTORY}{key}: {value}{Colors.ENDC}")
        print()
    
    def print_prompt_analysis(self, prompt_data: Dict[str, Any]):
        """Print prompt generation analysis"""
        print(f"{Colors.PROMPT}📝 PROMPT GENERATION ANALYSIS{Colors.ENDC}")
        
        prompt_length = len(prompt_data.get('prompt', ''))
        print(f"{Colors.PROMPT}Final Prompt Length: {prompt_length} chars{Colors.ENDC}")
        
        if 'components' in prompt_data:
            components = prompt_data['components']
            print(f"{Colors.PROMPT}Prompt Components:{Colors.ENDC}")
            for comp_name, comp_data in components.items():
                if isinstance(comp_data, dict) and 'length' in comp_data:
                    print(f"{Colors.PROMPT}   {comp_name}: {comp_data['length']} chars{Colors.ENDC}")
                else:
                    print(f"{Colors.PROMPT}   {comp_name}: {len(str(comp_data))} chars{Colors.ENDC}")
        
        if 'template_used' in prompt_data:
            print(f"{Colors.PROMPT}Template Used: {prompt_data['template_used']}{Colors.ENDC}")
        
        print()
    
    def print_security_analysis(self, security_data: Dict[str, Any]):
        """Print security anonymization analysis"""
        print(f"{Colors.SECURITY}🔒 SECURITY ANALYSIS{Colors.ENDC}")
        
        if 'anonymizations' in security_data:
            anon_count = len(security_data['anonymizations'])
            print(f"{Colors.SECURITY}Anonymizations Applied: {anon_count}{Colors.ENDC}")
            
            for i, anon in enumerate(security_data['anonymizations'][:5]):  # Show first 5
                print(f"{Colors.SECURITY}   {i+1}. {anon['original']} → {anon['anonymized']}{Colors.ENDC}")
                
        if 'prompt_sanitized' in security_data:
            print(f"{Colors.SECURITY}Prompt Sanitized: {security_data['prompt_sanitized']}{Colors.ENDC}")
            
        if 'response_deanonymized' in security_data:
            print(f"{Colors.SECURITY}Response De-anonymized: {security_data['response_deanonymized']}{Colors.ENDC}")
        
        print()
    
    def print_llm_analysis(self, llm_data: Dict[str, Any]):
        """Print LLM interaction analysis"""
        print(f"{Colors.LLM}🤖 LLM INTERACTION ANALYSIS{Colors.ENDC}")
        
        if 'model_name' in llm_data:
            print(f"{Colors.LLM}Model Used: {llm_data['model_name']}{Colors.ENDC}")
            
        if 'input_tokens' in llm_data:
            print(f"{Colors.LLM}Input Tokens: {llm_data['input_tokens']}{Colors.ENDC}")
            
        if 'output_tokens' in llm_data:
            print(f"{Colors.LLM}Output Tokens: {llm_data['output_tokens']}{Colors.ENDC}")
            
        if 'response_time' in llm_data:
            print(f"{Colors.LLM}Response Time: {llm_data['response_time']:.3f}s{Colors.ENDC}")
            
        if 'raw_response_length' in llm_data:
            print(f"{Colors.LLM}Raw Response Length: {llm_data['raw_response_length']} chars{Colors.ENDC}")
        
        print()
    
    def print_formatting_analysis(self, format_data: Dict[str, Any]):
        """Print response formatting analysis"""
        print(f"{Colors.FORMATTER}🎨 RESPONSE FORMATTING ANALYSIS{Colors.ENDC}")
        
        if 'parsing_method' in format_data:
            print(f"{Colors.FORMATTER}Parsing Method: {format_data['parsing_method']}{Colors.ENDC}")
            
        if 'json_extracted' in format_data:
            print(f"{Colors.FORMATTER}JSON Extracted: {format_data['json_extracted']}{Colors.ENDC}")
            
        if 'fields_found' in format_data:
            fields = format_data['fields_found']
            print(f"{Colors.FORMATTER}Fields Found: {', '.join(fields)}{Colors.ENDC}")
            
        if 'answer_length' in format_data:
            print(f"{Colors.FORMATTER}Answer Length: {format_data['answer_length']} chars{Colors.ENDC}")
            
        if 'followup_generated' in format_data:
            print(f"{Colors.FORMATTER}Followup Generated: {format_data['followup_generated']}{Colors.ENDC}")
        
        print()
    
    def print_final_summary(self, total_time: float, result: Dict[str, Any]):
        """Print final processing summary"""
        print(f"\n{Colors.BOLD}📋 PROCESSING SUMMARY{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*50}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Total Processing Time: {total_time:.3f}s{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Steps Completed: {len([s for s in self.steps if s.status == 'success'])}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Steps Failed: {len([s for s in self.steps if s.status == 'error'])}{Colors.ENDC}")
        
        # Show step timings
        print(f"\n{Colors.OKCYAN}Step Timing Breakdown:{Colors.ENDC}")
        for step in self.steps:
            status_color = Colors.OKGREEN if step.status == 'success' else Colors.FAIL
            status_icon = "✅" if step.status == 'success' else "❌"
            print(f"{status_color}{status_icon} {step.name}: {step.duration:.3f}s{Colors.ENDC}")
        
        # Show final result preview
        if result:
            print(f"\n{Colors.BOLD}📤 FINAL RESULT{Colors.ENDC}")
            if hasattr(result, 'answer'):
                answer_preview = result.answer[:200] + "..." if len(result.answer) > 200 else result.answer
                print(f"{Colors.OKGREEN}Answer: {answer_preview}{Colors.ENDC}")
                
            if hasattr(result, 'followup'):
                print(f"{Colors.OKGREEN}Followup: {result.followup}{Colors.ENDC}")
                
            if hasattr(result, 'org_related'):
                print(f"{Colors.OKGREEN}Org Related: {result.org_related}{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}{'='*50}{Colors.ENDC}\n")
    
    def clear_session(self):
        """Clear current session data"""
        self.steps.clear()
        self.current_step = None
        self.session_start_time = time.perf_counter()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_session_time = time.perf_counter() - self.session_start_time
        successful_steps = len([s for s in self.steps if s.status == 'success'])
        failed_steps = len([s for s in self.steps if s.status == 'error'])
        
        return {
            'total_queries': self.total_queries,
            'session_duration': total_session_time,
            'successful_steps': successful_steps,
            'failed_steps': failed_steps,
            'average_query_time': total_session_time / max(1, self.total_queries)
        }

# Global visualizer instance
visualizer = PipelineVisualizer()
