import time
import json
import re
from types import SimpleNamespace
from typing import Dict, Any
from src.utils.ResponseFormatter import ResponseFormatter
from src.inference.PipelineVisualizer import Colors

class EnhancedResponseFormatter(ResponseFormatter):
    """
    Enhanced Response Formatter with detailed visualization and analysis.
    Extends the original ResponseFormatter with comprehensive logging and metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.format_count = 0
        self.format_history = []
        print(f"{Colors.FORMATTER}✅ Enhanced Response Formatter initialized{Colors.ENDC}")
    
    def to_json_object_with_details(self, response_content: str) -> Dict[str, Any]:
        """
        Convert LLM response to JSON object with detailed analysis.
        """
        start_time = time.perf_counter()
        self.format_count += 1
        
        print(f"{Colors.FORMATTER}🎨 Response Formatting #{self.format_count}{Colors.ENDC}")
        print(f"{Colors.FORMATTER}Input length: {len(response_content)} chars{Colors.ENDC}")
        
        try:
            # Analyze the raw response
            raw_analysis = self._analyze_raw_response(response_content)
            print(f"{Colors.FORMATTER}Raw response type: {raw_analysis['response_type']}{Colors.ENDC}")
            
            # Apply the original formatting logic
            parsing_start = time.perf_counter()
            parsed_object = super().to_json_object(response_content)
            parsing_time = time.perf_counter() - parsing_start
            
            # Analyze the parsed result
            parsed_analysis = self._analyze_parsed_object(parsed_object)
            
            total_time = time.perf_counter() - start_time
            
            print(f"{Colors.FORMATTER}📊 Parsing completed in {parsing_time:.3f}s{Colors.ENDC}")
            print(f"{Colors.FORMATTER}📊 Fields extracted: {', '.join(parsed_analysis['fields_found'])}{Colors.ENDC}")
            
            # Determine parsing method used
            parsing_method = self._determine_parsing_method(response_content, raw_analysis)
            
            # Create detailed result
            result = {
                'parsed': parsed_object,
                'parsing_method': parsing_method,
                'json_extracted': raw_analysis['has_json'],
                'fields_found': parsed_analysis['fields_found'],
                'timings': {
                    'parsing_time': parsing_time,
                    'total_time': total_time
                },
                'raw_analysis': raw_analysis,
                'parsed_analysis': parsed_analysis,
                'format_number': self.format_count
            }
            
            # Store in history
            self.format_history.append({
                'input_length': len(response_content),
                'parsing_method': parsing_method,
                'fields_found': len(parsed_analysis['fields_found']),
                'parsing_time': parsing_time,
                'success': True,
                'has_json': raw_analysis['has_json'],
                'timestamp': time.time()
            })
            
            # Keep only last 100 formatting operations
            if len(self.format_history) > 100:
                self.format_history.pop(0)
            
            print(f"{Colors.FORMATTER}⚡ Response formatting completed in {total_time:.3f}s{Colors.ENDC}")
            
            return result
            
        except Exception as e:
            total_time = time.perf_counter() - start_time
            print(f"{Colors.FAIL}❌ Error in enhanced response formatting: {e}{Colors.ENDC}")
            
            # Create fallback object
            fallback_object = SimpleNamespace()
            fallback_object.answer = "I apologize, but I encountered an error processing the response."
            fallback_object.followup = "Is there anything else I can help you with?"
            fallback_object.org_related = False
            
            # Store error in history
            self.format_history.append({
                'input_length': len(response_content),
                'parsing_method': 'error_fallback',
                'fields_found': 3,  # fallback has 3 fields
                'parsing_time': 0.0,
                'success': False,
                'has_json': False,
                'error': str(e),
                'timestamp': time.time()
            })
            
            return {
                'parsed': fallback_object,
                'parsing_method': 'error_fallback',
                'json_extracted': False,
                'fields_found': ['answer', 'followup', 'org_related'],
                'error': str(e),
                'timings': {
                    'parsing_time': 0.0,
                    'total_time': total_time
                },
                'format_number': self.format_count
            }
    
    def _analyze_raw_response(self, response: str) -> Dict[str, Any]:
        """Analyze characteristics of the raw response"""
        # Check for JSON structure
        has_json = bool(re.search(r'\{.*\}', response, re.DOTALL))
        has_markdown_fences = '```' in response
        has_code_blocks = '```json' in response.lower()
        
        # Determine response type
        response_type = "unknown"
        if has_code_blocks:
            response_type = "markdown_json"
        elif has_json:
            response_type = "raw_json"
        elif has_markdown_fences:
            response_type = "markdown"
        else:
            response_type = "plain_text"
        
        # Count JSON-like structures
        json_matches = re.findall(r'\{[^{}]*\}', response)
        nested_json_matches = re.findall(r'\{.*\}', response, re.DOTALL)
        
        return {
            'length': len(response),
            'line_count': len(response.split('\n')),
            'has_json': has_json,
            'has_markdown_fences': has_markdown_fences,
            'has_code_blocks': has_code_blocks,
            'response_type': response_type,
            'json_block_count': len(json_matches),
            'nested_json_count': len(nested_json_matches)
        }
    
    def _analyze_parsed_object(self, obj: SimpleNamespace) -> Dict[str, Any]:
        """Analyze the parsed object structure"""
        fields_found = []
        field_lengths = {}
        
        for attr in dir(obj):
            if not attr.startswith('_'):
                value = getattr(obj, attr)
                if not callable(value):
                    fields_found.append(attr)
                    field_lengths[attr] = len(str(value)) if value else 0
        
        # Check for required fields
        required_fields = ['answer', 'followup']
        has_required_fields = all(field in fields_found for field in required_fields)
        
        # Analyze content
        answer_length = field_lengths.get('answer', 0)
        followup_length = field_lengths.get('followup', 0)
        
        return {
            'fields_found': fields_found,
            'field_count': len(fields_found),
            'field_lengths': field_lengths,
            'has_required_fields': has_required_fields,
            'answer_length': answer_length,
            'followup_length': followup_length,
            'has_org_related': 'org_related' in fields_found,
            'has_dept': 'dept' in fields_found,
            'total_content_length': sum(field_lengths.values())
        }
    
    def _determine_parsing_method(self, response: str, raw_analysis: Dict[str, Any]) -> str:
        """Determine which parsing method was likely used"""
        if raw_analysis['has_code_blocks']:
            return "markdown_extraction"
        elif raw_analysis['has_json'] and not raw_analysis['has_markdown_fences']:
            return "direct_json"
        elif raw_analysis['has_markdown_fences']:
            return "fence_extraction"
        else:
            return "regex_extraction"
    
    def get_formatting_statistics(self) -> Dict[str, Any]:
        """Get comprehensive formatting statistics"""
        if not self.format_history:
            return {'message': 'No formatting history available'}
        
        from collections import Counter
        
        total_formats = len(self.format_history)
        successful_formats = sum(1 for entry in self.format_history if entry['success'])
        
        # Method usage
        method_usage = Counter(entry['parsing_method'] for entry in self.format_history)
        
        # Success rate
        success_rate = (successful_formats / total_formats) * 100
        
        # Average metrics
        avg_input_length = sum(entry['input_length'] for entry in self.format_history) / total_formats
        avg_parsing_time = sum(entry['parsing_time'] for entry in self.format_history) / total_formats
        avg_fields_found = sum(entry['fields_found'] for entry in self.format_history) / total_formats
        
        # JSON detection rate
        json_detected = sum(1 for entry in self.format_history if entry['has_json'])
        json_detection_rate = (json_detected / total_formats) * 100
        
        # Recent performance (last 10 operations)
        recent_operations = self.format_history[-10:]
        recent_success_rate = (sum(1 for entry in recent_operations if entry['success']) / len(recent_operations)) * 100
        recent_avg_time = sum(entry['parsing_time'] for entry in recent_operations) / len(recent_operations)
        
        return {
            'total_operations': total_formats,
            'success_rate': success_rate,
            'successful_operations': successful_formats,
            'method_usage': dict(method_usage),
            'averages': {
                'input_length': avg_input_length,
                'parsing_time': avg_parsing_time,
                'fields_found': avg_fields_found
            },
            'json_detection_rate': json_detection_rate,
            'recent_performance': {
                'success_rate': recent_success_rate,
                'average_time': recent_avg_time
            }
        }
    
    def print_formatting_statistics(self):
        """Print beautiful formatting statistics"""
        stats = self.get_formatting_statistics()
        
        if 'message' in stats:
            print(f"{Colors.FORMATTER}{stats['message']}{Colors.ENDC}")
            return
        
        print(f"\n{Colors.FORMATTER}📊 RESPONSE FORMATTING STATISTICS{Colors.ENDC}")
        print(f"{Colors.FORMATTER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.FORMATTER}Total Operations: {stats['total_operations']}{Colors.ENDC}")
        print(f"{Colors.FORMATTER}Success Rate: {stats['success_rate']:.1f}%{Colors.ENDC}")
        print(f"{Colors.FORMATTER}JSON Detection Rate: {stats['json_detection_rate']:.1f}%{Colors.ENDC}")
        
        print(f"\n{Colors.FORMATTER}Parsing Method Usage:{Colors.ENDC}")
        for method, count in stats['method_usage'].items():
            percentage = (count / stats['total_operations']) * 100
            print(f"{Colors.FORMATTER}  {method}: {count} ({percentage:.1f}%){Colors.ENDC}")
        
        avg = stats['averages']
        print(f"\n{Colors.FORMATTER}Average Metrics:{Colors.ENDC}")
        print(f"{Colors.FORMATTER}  Input Length: {avg['input_length']:.0f} chars{Colors.ENDC}")
        print(f"{Colors.FORMATTER}  Parsing Time: {avg['parsing_time']:.3f}s{Colors.ENDC}")
        print(f"{Colors.FORMATTER}  Fields Found: {avg['fields_found']:.1f}{Colors.ENDC}")
        
        recent = stats['recent_performance']
        print(f"\n{Colors.FORMATTER}Recent Performance (last 10):{Colors.ENDC}")
        print(f"{Colors.FORMATTER}  Success Rate: {recent['success_rate']:.1f}%{Colors.ENDC}")
        print(f"{Colors.FORMATTER}  Average Time: {recent['average_time']:.3f}s{Colors.ENDC}")
        
        print(f"{Colors.FORMATTER}{'='*50}{Colors.ENDC}\n")
    
    # Keep original method for backward compatibility
    def to_json_object(self, response_content: str) -> SimpleNamespace:
        """Original to_json_object method for backward compatibility"""
        result = self.to_json_object_with_details(response_content)
        return result['parsed']
