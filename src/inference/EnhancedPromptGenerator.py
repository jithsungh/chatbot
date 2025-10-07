import time
from typing import Dict, Any, Optional
from src.inference.PromptGenerator import PromptGenerator
from src.inference.PipelineVisualizer import Colors

class EnhancedPromptGenerator(PromptGenerator):
    """
    Enhanced Prompt Generator with detailed visualization and analysis.
    Extends the original PromptGenerator with comprehensive logging and metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.generation_count = 0
        self.generation_history = []
        print(f"{Colors.PROMPT}✅ Enhanced Prompt Generator initialized{Colors.ENDC}")
    
    async def generate_prompt_with_details(
        self, 
        query: str, 
        dept: str, 
        context_text: str = "", 
        history_text: str = "", 
        last_context: str = "", 
        last_followup: str = ""
    ) -> Dict[str, Any]:
        """
        Generate prompt with detailed analysis and component breakdown.
        """
        start_time = time.perf_counter()
        self.generation_count += 1
        
        print(f"{Colors.PROMPT}📝 Prompt Generation #{self.generation_count}{Colors.ENDC}")
        print(f"{Colors.PROMPT}Department: {dept}{Colors.ENDC}")
        print(f"{Colors.PROMPT}Query length: {len(query)} chars{Colors.ENDC}")
        
        try:
            # Analyze input components
            components = {
                'query': {
                    'content': query,
                    'length': len(query),
                    'word_count': len(query.split())
                },
                'department': {
                    'content': dept,
                    'length': len(dept)
                },
                'context': {
                    'content': context_text,
                    'length': len(context_text),
                    'provided': bool(context_text.strip())
                },
                'history': {
                    'content': history_text,
                    'length': len(history_text),
                    'provided': bool(history_text.strip())
                },
                'last_context': {
                    'content': last_context,
                    'length': len(last_context) if last_context else 0,
                    'provided': bool(last_context)
                },
                'last_followup': {
                    'content': last_followup,
                    'length': len(last_followup) if last_followup else 0,
                    'provided': bool(last_followup)
                }
            }
            
            # Print component analysis
            print(f"{Colors.PROMPT}📊 Component Analysis:{Colors.ENDC}")
            for comp_name, comp_data in components.items():
                status = "✅" if comp_data.get('provided', comp_data['length'] > 0) else "❌"
                print(f"{Colors.PROMPT}   {status} {comp_name}: {comp_data['length']} chars{Colors.ENDC}")
            
            # Generate the actual prompt using the parent method
            generation_start = time.perf_counter()
            prompt = await super().generate_prompt(
                query=query,
                dept=dept,
                context_text=context_text,
                history_text=history_text,
                last_context=last_context,
                last_followup=last_followup
            )
            generation_time = time.perf_counter() - generation_start
            
            # Analyze the generated prompt
            prompt_analysis = self._analyze_prompt(prompt)
            template_used = self._determine_template_used(dept, bool(context_text.strip()))
            
            total_time = time.perf_counter() - start_time
            
            print(f"{Colors.PROMPT}📊 Generated prompt: {len(prompt)} chars in {generation_time:.3f}s{Colors.ENDC}")
            print(f"{Colors.PROMPT}📊 Template used: {template_used}{Colors.ENDC}")
            print(f"{Colors.PROMPT}📊 Sections found: {len(prompt_analysis['sections'])}{Colors.ENDC}")
            
            # Create detailed result
            result = {
                'prompt': prompt,
                'template_used': template_used,
                'components': components,
                'analysis': prompt_analysis,
                'timings': {
                    'generation_time': generation_time,
                    'total_time': total_time
                },
                'statistics': {
                    'total_length': len(prompt),
                    'word_count': len(prompt.split()),
                    'line_count': len(prompt.split('\n')),
                    'context_ratio': len(context_text) / len(prompt) if prompt else 0.0,
                    'history_ratio': len(history_text) / len(prompt) if prompt else 0.0
                },
                'generation_number': self.generation_count
            }
            
            # Store in history
            self.generation_history.append({
                'department': dept,
                'template_used': template_used,
                'prompt_length': len(prompt),
                'context_provided': bool(context_text.strip()),
                'history_provided': bool(history_text.strip()),
                'generation_time': generation_time,
                'timestamp': time.time()
            })
            
            # Keep only last 100 generations
            if len(self.generation_history) > 100:
                self.generation_history.pop(0)
            
            print(f"{Colors.PROMPT}⚡ Prompt generation completed in {total_time:.3f}s{Colors.ENDC}")
            
            return result
            
        except Exception as e:
            total_time = time.perf_counter() - start_time
            print(f"{Colors.FAIL}❌ Error in enhanced prompt generation: {e}{Colors.ENDC}")
            
            # Fallback to basic prompt
            fallback_prompt = f"""You are a helpful AI assistant for Techmojo company.
            
            Department: {dept}
            Question: {query}

            Please provide a helpful and accurate response."""
            
            return {
                'prompt': fallback_prompt,
                'template_used': 'fallback',
                'components': components,
                'error': str(e),
                'timings': {
                    'generation_time': 0.0,
                    'total_time': total_time
                },
                'generation_number': self.generation_count
            }
    
    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze the structure and content of the generated prompt"""
        lines = prompt.split('\n')
        sections = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('#') or line.isupper() or line.endswith(':'):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'title': line,
                    'content_lines': 0,
                    'content_chars': 0
                }
            elif current_section and line:
                current_section['content_lines'] += 1
                current_section['content_chars'] += len(line)
        
        if current_section:
            sections.append(current_section)
        
        return {
            'sections': sections,
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'has_system_message': 'system' in prompt.lower() or 'assistant' in prompt.lower(),
            'has_context': 'context' in prompt.lower(),
            'has_history': 'history' in prompt.lower() or 'previous' in prompt.lower(),
            'has_instructions': 'instructions' in prompt.lower() or 'rules' in prompt.lower()
        }
    
    def _determine_template_used(self, dept: str, has_context: bool) -> str:
        """Determine which template was likely used based on inputs"""
        if has_context:
            return f"{dept}_with_context"
        else:
            return f"{dept}_no_context"
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive prompt generation statistics"""
        if not self.generation_history:
            return {'message': 'No generation history available'}
        
        from collections import Counter
        
        total_generations = len(self.generation_history)
        
        # Template usage
        template_usage = Counter(entry['template_used'] for entry in self.generation_history)
        
        # Department usage
        dept_usage = Counter(entry['department'] for entry in self.generation_history)
        
        # Context/History usage
        context_provided = sum(1 for entry in self.generation_history if entry['context_provided'])
        history_provided = sum(1 for entry in self.generation_history if entry['history_provided'])
        
        # Average metrics
        avg_prompt_length = sum(entry['prompt_length'] for entry in self.generation_history) / total_generations
        avg_generation_time = sum(entry['generation_time'] for entry in self.generation_history) / total_generations
        
        # Recent performance (last 10 generations)
        recent_generations = self.generation_history[-10:]
        recent_avg_time = sum(entry['generation_time'] for entry in recent_generations) / len(recent_generations)
        recent_avg_length = sum(entry['prompt_length'] for entry in recent_generations) / len(recent_generations)
        
        return {
            'total_generations': total_generations,
            'template_usage': dict(template_usage),
            'department_usage': dict(dept_usage),
            'context_usage': {
                'context_provided': context_provided,
                'context_percentage': (context_provided / total_generations) * 100,
                'history_provided': history_provided,
                'history_percentage': (history_provided / total_generations) * 100
            },
            'averages': {
                'prompt_length': avg_prompt_length,
                'generation_time': avg_generation_time
            },
            'recent_performance': {
                'average_time': recent_avg_time,
                'average_length': recent_avg_length
            }
        }
    
    def print_generation_statistics(self):
        """Print beautiful generation statistics"""
        stats = self.get_generation_statistics()
        
        if 'message' in stats:
            print(f"{Colors.PROMPT}{stats['message']}{Colors.ENDC}")
            return
        
        print(f"\n{Colors.PROMPT}📊 PROMPT GENERATION STATISTICS{Colors.ENDC}")
        print(f"{Colors.PROMPT}{'='*50}{Colors.ENDC}")
        print(f"{Colors.PROMPT}Total Generations: {stats['total_generations']}{Colors.ENDC}")
        print(f"{Colors.PROMPT}Average Prompt Length: {stats['averages']['prompt_length']:.0f} chars{Colors.ENDC}")
        print(f"{Colors.PROMPT}Average Generation Time: {stats['averages']['generation_time']:.3f}s{Colors.ENDC}")
        
        print(f"\n{Colors.PROMPT}Template Usage:{Colors.ENDC}")
        for template, count in stats['template_usage'].items():
            percentage = (count / stats['total_generations']) * 100
            print(f"{Colors.PROMPT}  {template}: {count} ({percentage:.1f}%){Colors.ENDC}")
        
        print(f"\n{Colors.PROMPT}Department Usage:{Colors.ENDC}")
        for dept, count in stats['department_usage'].items():
            percentage = (count / stats['total_generations']) * 100
            print(f"{Colors.PROMPT}  {dept}: {count} ({percentage:.1f}%){Colors.ENDC}")
        
        context_usage = stats['context_usage']
        print(f"\n{Colors.PROMPT}Content Usage:{Colors.ENDC}")
        print(f"{Colors.PROMPT}  Context Provided: {context_usage['context_percentage']:.1f}%{Colors.ENDC}")
        print(f"{Colors.PROMPT}  History Provided: {context_usage['history_percentage']:.1f}%{Colors.ENDC}")
        
        recent = stats['recent_performance']
        print(f"\n{Colors.PROMPT}Recent Performance (last 10):{Colors.ENDC}")
        print(f"{Colors.PROMPT}  Average Time: {recent['average_time']:.3f}s{Colors.ENDC}")
        print(f"{Colors.PROMPT}  Average Length: {recent['average_length']:.0f} chars{Colors.ENDC}")
        
        print(f"{Colors.PROMPT}{'='*50}{Colors.ENDC}\n")
