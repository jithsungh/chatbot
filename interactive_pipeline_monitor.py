"""
Interactive Pipeline Monitor

A real-time monitoring tool for the inference pipeline that can be used alongside your existing
Pipeline.py without major changes. This provides live visualization of query processing.

Usage:
1. Import this module in your main application
2. Call monitor_query() to track individual queries
3. Use the interactive monitor for real-time visualization
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.inference.PipelineVisualizer import visualizer, Colors

class PipelineMonitor:
    """
    Real-time pipeline monitoring system that can integrate with your existing Pipeline.py
    """
    
    def __init__(self):
        self.active_queries = {}
        self.completed_queries = []
        self.monitoring_enabled = True
        
    def start_query_monitoring(self, query_id: str, query: str, userid: str):
        """Start monitoring a new query"""
        if not self.monitoring_enabled:
            return
            
        self.active_queries[query_id] = {
            'query': query,
            'userid': userid,
            'start_time': time.perf_counter(),
            'steps': [],
            'current_step': None
        }
        
        print(f"\n{Colors.OKCYAN}🔍 Starting to monitor query: {query_id}{Colors.ENDC}")
        visualizer.print_query_header(query, userid)
    
    def log_step_start(self, query_id: str, step_name: str, step_data: Dict[str, Any] = None):
        """Log the start of a pipeline step"""
        if not self.monitoring_enabled or query_id not in self.active_queries:
            return
            
        step_info = {
            'name': step_name,
            'start_time': time.perf_counter(),
            'data': step_data or {},
            'status': 'running'
        }
        
        self.active_queries[query_id]['steps'].append(step_info)
        self.active_queries[query_id]['current_step'] = len(self.active_queries[query_id]['steps']) - 1
        
        # Get color for step
        color = self._get_step_color(step_name)
        print(f"{color}🔄 {step_name}...{Colors.ENDC}")
        
        return len(self.active_queries[query_id]['steps']) - 1  # Return step index
    
    def log_step_complete(self, query_id: str, step_index: int, result_data: Dict[str, Any] = None):
        """Log the completion of a pipeline step"""
        if not self.monitoring_enabled or query_id not in self.active_queries:
            return
            
        query_info = self.active_queries[query_id]
        if step_index < len(query_info['steps']):
            step = query_info['steps'][step_index]
            step['end_time'] = time.perf_counter()
            step['duration'] = step['end_time'] - step['start_time']
            step['status'] = 'completed'
            step['result'] = result_data or {}
            
            color = self._get_step_color(step['name'])
            print(f"{Colors.OKGREEN}✅ {step['name']} completed in {step['duration']:.3f}s{Colors.ENDC}")
    
    def log_step_error(self, query_id: str, step_index: int, error: str):
        """Log an error in a pipeline step"""
        if not self.monitoring_enabled or query_id not in self.active_queries:
            return
            
        query_info = self.active_queries[query_id]
        if step_index < len(query_info['steps']):
            step = query_info['steps'][step_index]
            step['end_time'] = time.perf_counter()
            step['duration'] = step['end_time'] - step['start_time']
            step['status'] = 'error'
            step['error'] = error
            
            print(f"{Colors.FAIL}❌ {step['name']} failed after {step['duration']:.3f}s: {error}{Colors.ENDC}")
    
    def complete_query_monitoring(self, query_id: str, final_result: Any = None):
        """Complete monitoring for a query"""
        if not self.monitoring_enabled or query_id not in self.active_queries:
            return
            
        query_info = self.active_queries[query_id]
        query_info['end_time'] = time.perf_counter()
        query_info['total_duration'] = query_info['end_time'] - query_info['start_time']
        query_info['final_result'] = final_result
        
        # Move to completed queries
        self.completed_queries.append(query_info)
        del self.active_queries[query_id]
        
        # Keep only last 100 completed queries
        if len(self.completed_queries) > 100:
            self.completed_queries.pop(0)
        
        # Print summary
        self._print_query_summary(query_info)
    
    def _get_step_color(self, step_name: str) -> str:
        """Get color for different step types"""
        step_colors = {
            'routing': Colors.ROUTER,
            'department': Colors.ROUTER,
            'context': Colors.RETRIEVER,
            'retrieval': Colors.RETRIEVER,
            'history': Colors.HISTORY,
            'prompt': Colors.PROMPT,
            'llm': Colors.LLM,
            'security': Colors.SECURITY,
            'format': Colors.FORMATTER,
            'response': Colors.FORMATTER
        }
        
        for keyword, color in step_colors.items():
            if keyword in step_name.lower():
                return color
        
        return Colors.OKGREEN
    
    def _print_query_summary(self, query_info: Dict[str, Any]):
        """Print a summary of the completed query"""
        print(f"\n{Colors.BOLD}📋 QUERY PROCESSING SUMMARY{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*50}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Total Processing Time: {query_info['total_duration']:.3f}s{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Steps Completed: {len([s for s in query_info['steps'] if s['status'] == 'completed'])}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Steps Failed: {len([s for s in query_info['steps'] if s['status'] == 'error'])}{Colors.ENDC}")
        
        print(f"\n{Colors.OKCYAN}Step Timing Breakdown:{Colors.ENDC}")
        for step in query_info['steps']:
            status_color = Colors.OKGREEN if step['status'] == 'completed' else Colors.FAIL
            status_icon = "✅" if step['status'] == 'completed' else "❌"
            duration = step.get('duration', 0)
            print(f"{status_color}{status_icon} {step['name']}: {duration:.3f}s{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}{'='*50}{Colors.ENDC}\n")
    
    def get_live_statistics(self) -> Dict[str, Any]:
        """Get live monitoring statistics"""
        completed_count = len(self.completed_queries)
        active_count = len(self.active_queries)
        
        if completed_count == 0:
            return {
                'active_queries': active_count,
                'completed_queries': 0,
                'message': 'No completed queries yet'
            }
        
        # Calculate averages from completed queries
        total_time = sum(q['total_duration'] for q in self.completed_queries)
        avg_time = total_time / completed_count
        
        successful_queries = sum(
            1 for q in self.completed_queries 
            if all(s['status'] == 'completed' for s in q['steps'])
        )
        success_rate = (successful_queries / completed_count) * 100
        
        # Step statistics
        all_steps = []
        for query in self.completed_queries:
            all_steps.extend(query['steps'])
        
        step_names = list(set(step['name'] for step in all_steps))
        step_stats = {}
        
        for step_name in step_names:
            step_instances = [s for s in all_steps if s['name'] == step_name]
            completed_instances = [s for s in step_instances if s['status'] == 'completed']
            
            if completed_instances:
                avg_duration = sum(s['duration'] for s in completed_instances) / len(completed_instances)
                success_rate_step = (len(completed_instances) / len(step_instances)) * 100
                
                step_stats[step_name] = {
                    'average_duration': avg_duration,
                    'success_rate': success_rate_step,
                    'total_executions': len(step_instances)
                }
        
        return {
            'active_queries': active_count,
            'completed_queries': completed_count,
            'average_query_time': avg_time,
            'overall_success_rate': success_rate,
            'step_statistics': step_stats
        }
    
    def print_live_dashboard(self):
        """Print a live dashboard of pipeline performance"""
        stats = self.get_live_statistics()
        
        print(f"\n{Colors.HEADER}📊 LIVE PIPELINE DASHBOARD{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Timestamp: {datetime.now().strftime('%H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Active Queries: {stats['active_queries']}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Completed Queries: {stats['completed_queries']}{Colors.ENDC}")
        
        if 'message' not in stats:
            print(f"{Colors.OKCYAN}Average Query Time: {stats['average_query_time']:.3f}s{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Overall Success Rate: {stats['overall_success_rate']:.1f}%{Colors.ENDC}")
            
            if stats['step_statistics']:
                print(f"\n{Colors.BOLD}Step Performance:{Colors.ENDC}")
                for step_name, step_stat in stats['step_statistics'].items():
                    color = self._get_step_color(step_name)
                    print(f"{color}{step_name}: {step_stat['average_duration']:.3f}s avg, {step_stat['success_rate']:.1f}% success{Colors.ENDC}")
        
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

# Global monitor instance
monitor = PipelineMonitor()

# Convenience functions for easy integration
def track_query(query: str, userid: str) -> str:
    """Start tracking a query and return a query ID"""
    query_id = f"query_{int(time.time() * 1000)}"
    monitor.start_query_monitoring(query_id, query, userid)
    return query_id

def log_step(query_id: str, step_name: str, data: Dict[str, Any] = None) -> int:
    """Log a step start"""
    return monitor.log_step_start(query_id, step_name, data)

def complete_step(query_id: str, step_index: int, result: Dict[str, Any] = None):
    """Mark a step as completed"""
    monitor.log_step_complete(query_id, step_index, result)

def error_step(query_id: str, step_index: int, error: str):
    """Mark a step as errored"""
    monitor.log_step_error(query_id, step_index, error)

def finish_query(query_id: str, result: Any = None):
    """Complete query tracking"""
    monitor.complete_query_monitoring(query_id, result)

def show_dashboard():
    """Show the live dashboard"""
    monitor.print_live_dashboard()

# Example integration with existing Pipeline.py
def integrate_with_existing_pipeline():
    """
    Example of how to integrate with your existing Pipeline.py
    
    In your Pipeline.process_user_query method, add calls like:
    
    async def process_user_query(self, query: str, userid: str) -> Dict[str, Any]:
        # Start tracking
        query_id = track_query(query, userid)
        
        try:
            # 1) Determine department
            step_idx = log_step(query_id, "Department Routing")
            dept = self.router.route_query(query)
            complete_step(query_id, step_idx, {"department": dept})
            
            # 2) Retrieve context
            step_idx = log_step(query_id, "Context Retrieval")
            chunks = self.retriever.retrieve_context(query=query, dept=dept, k=10)
            complete_step(query_id, step_idx, {"chunks_found": len(chunks)})
            
            # ... continue for other steps
            
            # Finish tracking
            finish_query(query_id, result)
            return result
            
        except Exception as e:
            error_step(query_id, step_idx, str(e))
            finish_query(query_id)
            raise
    """
    print(f"{Colors.OKGREEN}See the docstring of this function for integration examples{Colors.ENDC}")

if __name__ == "__main__":
    # Demo of the monitoring system
    print(f"{Colors.HEADER}🖥️ Interactive Pipeline Monitor Demo{Colors.ENDC}\n")
    
    # Simulate some queries
    query_id1 = track_query("How much advanced Salary I can Take?", "user001")
    
    step1 = log_step(query_id1, "Department Routing", {"query_length": 20})
    time.sleep(0.1)
    complete_step(query_id1, step1, {"department": "HR"})
    
    step2 = log_step(query_id1, "Context Retrieval")
    time.sleep(0.2)
    complete_step(query_id1, step2, {"chunks_found": 5})
    
    step3 = log_step(query_id1, "LLM Processing")
    time.sleep(0.5)
    complete_step(query_id1, step3, {"response_length": 150})
    
    finish_query(query_id1, {"answer": "Sample answer", "followup": "Any other questions?"})
    
    show_dashboard()
    
    print(f"{Colors.BOLD}Integration Instructions:{Colors.ENDC}")
    integrate_with_existing_pipeline()
