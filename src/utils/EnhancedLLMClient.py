import time
from typing import Dict, Any
from src.utils.LLMClientServer import LLMClientServer
from src.inference.PipelineVisualizer import Colors

class EnhancedLLMClient(LLMClientServer):
    """
    Enhanced LLM Client with detailed visualization and analysis.
    Extends the original LLMClientServer with comprehensive logging and metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.request_count = 0
        self.request_history = []
        print(f"{Colors.LLM}✅ Enhanced LLM Client initialized{Colors.ENDC}")
    
    def get_response_with_details(self, prompt: str) -> Dict[str, Any]:
        """
        Get LLM response with detailed analysis and metrics.
        """
        start_time = time.perf_counter()
        self.request_count += 1
        
        print(f"{Colors.LLM}🤖 LLM Request #{self.request_count}{Colors.ENDC}")
        print(f"{Colors.LLM}Prompt length: {len(prompt)} chars{Colors.ENDC}")
        
        # Analyze prompt
        prompt_analysis = self._analyze_prompt(prompt)
        print(f"{Colors.LLM}Estimated tokens: ~{prompt_analysis['estimated_tokens']}{Colors.ENDC}")
        
        try:
            # Get the actual response using parent method
            request_start = time.perf_counter()
            response = super().get_response(prompt)
            request_time = time.perf_counter() - request_start
            
            # Analyze response
            response_analysis = self._analyze_response(response)
            
            total_time = time.perf_counter() - start_time
            
            print(f"{Colors.LLM}📊 Response received: {len(response)} chars in {request_time:.3f}s{Colors.ENDC}")
            print(f"{Colors.LLM}📊 Estimated output tokens: ~{response_analysis['estimated_tokens']}{Colors.ENDC}")
            print(f"{Colors.LLM}📊 Tokens per second: ~{response_analysis['estimated_tokens']/request_time:.0f}{Colors.ENDC}")
            
            # Try to get model information
            model_name = self._get_model_name()
            
            # Create detailed result
            result = {
                'response': response,
                'model_name': model_name,
                'timings': {
                    'request_time': request_time,
                    'total_time': total_time
                },
                'prompt_analysis': prompt_analysis,
                'response_analysis': response_analysis,
                'performance': {
                    'tokens_per_second': response_analysis['estimated_tokens'] / request_time if request_time > 0 else 0,
                    'chars_per_second': len(response) / request_time if request_time > 0 else 0
                },
                'request_number': self.request_count
            }
            
            # Store in history
            self.request_history.append({
                'prompt_length': len(prompt),
                'response_length': len(response),
                'request_time': request_time,
                'estimated_input_tokens': prompt_analysis['estimated_tokens'],
                'estimated_output_tokens': response_analysis['estimated_tokens'],
                'model_name': model_name,
                'timestamp': time.time()
            })
            
            # Keep only last 100 requests
            if len(self.request_history) > 100:
                self.request_history.pop(0)
            
            print(f"{Colors.LLM}⚡ LLM processing completed in {total_time:.3f}s{Colors.ENDC}")
            
            return result
            
        except Exception as e:
            total_time = time.perf_counter() - start_time
            print(f"{Colors.FAIL}❌ Error in enhanced LLM request: {e}{Colors.ENDC}")
            
            return {
                'response': f"Error: {str(e)}",
                'model_name': 'unknown',
                'error': str(e),
                'timings': {
                    'request_time': 0.0,
                    'total_time': total_time
                },
                'request_number': self.request_count
            }
    
    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt characteristics"""
        words = prompt.split()
        lines = prompt.split('\n')
        
        # Estimate tokens (rough approximation: 1 token ≈ 0.75 words)
        estimated_tokens = int(len(words) * 1.33)
        
        return {
            'length': len(prompt),
            'word_count': len(words),
            'line_count': len(lines),
            'estimated_tokens': estimated_tokens,
            'has_system_prompt': any(line.strip().startswith('System:') or line.strip().startswith('You are') for line in lines),
            'has_context': 'context' in prompt.lower(),
            'has_examples': 'example' in prompt.lower() or 'sample' in prompt.lower()
        }
    
    def _analyze_response(self, response: str) -> Dict[str, Any]:
        """Analyze response characteristics"""
        words = response.split()
        lines = response.split('\n')
        
        # Estimate tokens
        estimated_tokens = int(len(words) * 1.33)
        
        # Check if response looks like JSON
        is_json_like = response.strip().startswith('{') and response.strip().endswith('}')
        
        return {
            'length': len(response),
            'word_count': len(words),
            'line_count': len(lines),
            'estimated_tokens': estimated_tokens,
            'is_json_like': is_json_like,
            'has_code_blocks': '```' in response,
            'has_markdown': any(marker in response for marker in ['**', '*', '#', '`'])
        }
    
    def _get_model_name(self) -> str:
        """Try to determine the model name"""
        # This is a placeholder - implement based on your actual LLM client
        # You might need to check configuration or add model info to the parent class
        try:
            if hasattr(self, 'model_name'):
                return self.model_name
            elif hasattr(self, 'config') and hasattr(self.config, 'MODEL_NAME'):
                return self.config.MODEL_NAME
            else:
                return "Unknown Model"
        except:
            return "Unknown Model"
    
    def get_llm_statistics(self) -> Dict[str, Any]:
        """Get comprehensive LLM usage statistics"""
        if not self.request_history:
            return {'message': 'No request history available'}
        
        total_requests = len(self.request_history)
        
        # Calculate averages
        avg_prompt_length = sum(entry['prompt_length'] for entry in self.request_history) / total_requests
        avg_response_length = sum(entry['response_length'] for entry in self.request_history) / total_requests
        avg_request_time = sum(entry['request_time'] for entry in self.request_history) / total_requests
        
        # Token statistics
        total_input_tokens = sum(entry['estimated_input_tokens'] for entry in self.request_history)
        total_output_tokens = sum(entry['estimated_output_tokens'] for entry in self.request_history)
        avg_tokens_per_second = sum(
            entry['estimated_output_tokens'] / entry['request_time'] if entry['request_time'] > 0 else 0
            for entry in self.request_history
        ) / total_requests
        
        # Recent performance (last 10 requests)
        recent_requests = self.request_history[-10:]
        recent_avg_time = sum(entry['request_time'] for entry in recent_requests) / len(recent_requests)
        recent_avg_tokens_per_sec = sum(
            entry['estimated_output_tokens'] / entry['request_time'] if entry['request_time'] > 0 else 0
            for entry in recent_requests
        ) / len(recent_requests)
        
        # Model usage
        from collections import Counter
        model_usage = Counter(entry['model_name'] for entry in self.request_history)
        
        return {
            'total_requests': total_requests,
            'averages': {
                'prompt_length': avg_prompt_length,
                'response_length': avg_response_length,
                'request_time': avg_request_time,
                'tokens_per_second': avg_tokens_per_second
            },
            'token_usage': {
                'total_input_tokens': total_input_tokens,
                'total_output_tokens': total_output_tokens,
                'average_input_tokens': total_input_tokens / total_requests,
                'average_output_tokens': total_output_tokens / total_requests
            },
            'model_usage': dict(model_usage),
            'recent_performance': {
                'average_time': recent_avg_time,
                'average_tokens_per_second': recent_avg_tokens_per_sec
            }
        }
    
    def print_llm_statistics(self):
        """Print beautiful LLM statistics"""
        stats = self.get_llm_statistics()
        
        if 'message' in stats:
            print(f"{Colors.LLM}{stats['message']}{Colors.ENDC}")
            return
        
        print(f"\n{Colors.LLM}📊 LLM CLIENT STATISTICS{Colors.ENDC}")
        print(f"{Colors.LLM}{'='*50}{Colors.ENDC}")
        print(f"{Colors.LLM}Total Requests: {stats['total_requests']}{Colors.ENDC}")
        
        avg = stats['averages']
        print(f"\n{Colors.LLM}Average Metrics:{Colors.ENDC}")
        print(f"{Colors.LLM}  Prompt Length: {avg['prompt_length']:.0f} chars{Colors.ENDC}")
        print(f"{Colors.LLM}  Response Length: {avg['response_length']:.0f} chars{Colors.ENDC}")
        print(f"{Colors.LLM}  Request Time: {avg['request_time']:.3f}s{Colors.ENDC}")
        print(f"{Colors.LLM}  Tokens/Second: {avg['tokens_per_second']:.0f}{Colors.ENDC}")
        
        tokens = stats['token_usage']
        print(f"\n{Colors.LLM}Token Usage:{Colors.ENDC}")
        print(f"{Colors.LLM}  Total Input Tokens: {tokens['total_input_tokens']:,}{Colors.ENDC}")
        print(f"{Colors.LLM}  Total Output Tokens: {tokens['total_output_tokens']:,}{Colors.ENDC}")
        print(f"{Colors.LLM}  Avg Input Tokens: {tokens['average_input_tokens']:.0f}{Colors.ENDC}")
        print(f"{Colors.LLM}  Avg Output Tokens: {tokens['average_output_tokens']:.0f}{Colors.ENDC}")
        
        print(f"\n{Colors.LLM}Model Usage:{Colors.ENDC}")
        for model, count in stats['model_usage'].items():
            percentage = (count / stats['total_requests']) * 100
            print(f"{Colors.LLM}  {model}: {count} ({percentage:.1f}%){Colors.ENDC}")
        
        recent = stats['recent_performance']
        print(f"\n{Colors.LLM}Recent Performance (last 10):{Colors.ENDC}")
        print(f"{Colors.LLM}  Average Time: {recent['average_time']:.3f}s{Colors.ENDC}")
        print(f"{Colors.LLM}  Average Tokens/Sec: {recent['average_tokens_per_second']:.0f}{Colors.ENDC}")
        
        print(f"{Colors.LLM}{'='*50}{Colors.ENDC}\n")
    
    # Keep original method for backward compatibility
    def get_response(self, prompt: str) -> str:
        """Original get_response method for backward compatibility"""
        result = self.get_response_with_details(prompt)
        return result['response']
