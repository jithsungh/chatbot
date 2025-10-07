"""
Enhanced Pipeline Visualization Demo

This script demonstrates the comprehensive visualization system for the inference pipeline.
It shows every step of query processing with beautiful console output, detailed timing,
and comprehensive analysis.

Run this script to see the complete pipeline visualization in action!
"""

import asyncio
import time
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.inference.EnhancedPipeline import EnhancedPipeline
from src.inference.PipelineVisualizer import visualizer, Colors

async def demo_queries():
    """Demonstrate the enhanced pipeline with various types of queries"""
    
    # Initialize the enhanced pipeline
    pipeline = EnhancedPipeline()
    
    # Test queries representing different scenarios
    test_queries = [
        {
            "query": "What is the referral Bonus policy?",
            "userid": "demo_user_001",
            "description": "HR Department Query with Context Expected"
        },
    ]
    
    print(f"\n{Colors.HEADER}🎯 PIPELINE VISUALIZATION DEMO{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}This demo will process {len(test_queries)} different types of queries{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Each query will show the complete pipeline flow with timing and analysis{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    # Process each test query
    for i, query_info in enumerate(test_queries, 1):
        print(f"\n{Colors.BOLD}🔥 PROCESSING QUERY {i}/{len(test_queries)}{Colors.ENDC}")
        print(f"{Colors.BOLD}📋 Scenario: {query_info['description']}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'🔄'*60}{Colors.ENDC}\n")
        
        # Add a small delay for dramatic effect
        await asyncio.sleep(1)
        
        # Process the query
        try:
            result = await pipeline.process_user_query(
                query_info["query"], 
                query_info["userid"]
            )
              # Show the final result
            print(f"\n{Colors.OKGREEN}✨ FINAL RESULT FOR QUERY {i}{Colors.ENDC}")
            
            # Handle both SimpleNamespace objects and dictionaries
            if hasattr(result, 'answer'):
                answer = result.answer
                followup = getattr(result, 'followup', 'No follow-up available')
            elif isinstance(result, dict):
                answer = result.get('answer', 'No answer available')
                followup = result.get('followup', 'No follow-up available')
            else:
                answer = str(result)
                followup = 'No follow-up available'
            
            print(f"{Colors.OKGREEN}Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Follow-up: {followup}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error processing query {i}: {e}{Colors.ENDC}")
        
        # Add separator between queries
        if i < len(test_queries):
            print(f"\n{Colors.WARNING}{'⏭'*80}{Colors.ENDC}")
            print(f"{Colors.WARNING}Moving to next query...{Colors.ENDC}")
            print(f"{Colors.WARNING}{'⏭'*80}{Colors.ENDC}\n")
            await asyncio.sleep(2)
    
    # Print final session statistics
    print_final_demo_summary(pipeline)

def print_final_demo_summary(pipeline):
    """Print comprehensive demo summary with statistics"""
    
    print(f"\n{Colors.HEADER}{'🎊'*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🏆 DEMO COMPLETION SUMMARY 🏆{Colors.ENDC}")
    print(f"{Colors.HEADER}{'🎊'*80}{Colors.ENDC}")
    
    # Get session stats
    session_stats = pipeline.get_performance_stats()
    
    print(f"\n{Colors.BOLD}📊 SESSION STATISTICS{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Total Queries Processed: {session_stats['total_queries']}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Session Duration: {session_stats['session_duration']:.2f} seconds{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Average Query Time: {session_stats['average_query_time']:.3f} seconds{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Successful Steps: {session_stats['successful_steps']}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Failed Steps: {session_stats['failed_steps']}{Colors.ENDC}")
    
    # Print component statistics if available
    print(f"\n{Colors.BOLD}🔧 COMPONENT PERFORMANCE{Colors.ENDC}")
    
    # Router statistics
    if hasattr(pipeline.router, 'print_routing_statistics'):
        pipeline.router.print_routing_statistics()
    
    # Retriever statistics  
    if hasattr(pipeline.retriever, 'print_retrieval_statistics'):
        pipeline.retriever.print_retrieval_statistics()
    
    # LLM Client statistics
    if hasattr(pipeline.llm_client, 'print_llm_statistics'):
        pipeline.llm_client.print_llm_statistics()
    
    # Response Formatter statistics
    if hasattr(pipeline.response_formatter, 'print_formatting_statistics'):
        pipeline.response_formatter.print_formatting_statistics()
    
    print(f"\n{Colors.HEADER}{'🎉'*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🌟 VISUALIZATION DEMO COMPLETED SUCCESSFULLY! 🌟{Colors.ENDC}")
    print(f"{Colors.HEADER}{'🎉'*80}{Colors.ENDC}")
    
    # Provide next steps
    print(f"\n{Colors.BOLD}🚀 WHAT'S NEXT?{Colors.ENDC}")
    print(f"{Colors.OKGREEN}1. Use EnhancedPipeline in your main application for detailed monitoring{Colors.ENDC}")
    print(f"{Colors.OKGREEN}2. Review the component statistics to optimize performance{Colors.ENDC}")
    print(f"{Colors.OKGREEN}3. Use the visualization system for debugging and analysis{Colors.ENDC}")
    print(f"{Colors.OKGREEN}4. Customize the colors and output format as needed{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}📁 FILES CREATED:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• src/inference/PipelineVisualizer.py - Core visualization system{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• src/inference/EnhancedPipeline.py - Enhanced pipeline with visualization{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• src/inference/EnhancedRouter.py - Enhanced router with detailed analysis{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• src/inference/EnhancedRetriever.py - Enhanced retriever with metrics{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• src/inference/EnhancedPromptGenerator.py - Enhanced prompt generator{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• src/utils/EnhancedLLMClient.py - Enhanced LLM client with analysis{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• src/utils/EnhancedResponseFormatter.py - Enhanced formatter{Colors.ENDC}")
    print(f"{Colors.OKCYAN}• visualization_demo.py - This demonstration script{Colors.ENDC}")

def print_intro():
    """Print introduction and setup information"""
    print(f"{Colors.HEADER}{'🌟'*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}✨ ENHANCED INFERENCE PIPELINE VISUALIZATION ✨{Colors.ENDC}")
    print(f"{Colors.HEADER}{'🌟'*80}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}🎯 WHAT THIS DEMO SHOWS:{Colors.ENDC}")
    print(f"{Colors.OKGREEN}• Complete query processing flow from start to finish{Colors.ENDC}")
    print(f"{Colors.OKGREEN}• Detailed timing analysis for each pipeline step{Colors.ENDC}")
    print(f"{Colors.OKGREEN}• Beautiful colored console output with step-by-step progress{Colors.ENDC}")
    print(f"{Colors.OKGREEN}• Component-specific analysis and statistics{Colors.ENDC}")
    print(f"{Colors.OKGREEN}• Performance metrics and optimization insights{Colors.ENDC}")
    print(f"{Colors.OKGREEN}• Error handling and fallback mechanisms{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}🔧 PIPELINE COMPONENTS VISUALIZED:{Colors.ENDC}")
    print(f"{Colors.ROUTER}1. Department Routing - Query classification and analysis{Colors.ENDC}")
    print(f"{Colors.RETRIEVER}2. Context Retrieval - Vector search and document retrieval{Colors.ENDC}")
    print(f"{Colors.HISTORY}3. History Management - Conversation context and state{Colors.ENDC}")
    print(f"{Colors.PROMPT}4. Prompt Generation - Template selection and content assembly{Colors.ENDC}")
    print(f"{Colors.SECURITY}5. Security Processing - Anonymization and sanitization{Colors.ENDC}")
    print(f"{Colors.LLM}6. LLM Processing - Model inference and response generation{Colors.ENDC}")
    print(f"{Colors.FORMATTER}7. Response Formatting - JSON parsing and structure validation{Colors.ENDC}")
    
    print(f"\n{Colors.WARNING}⚠️ REQUIREMENTS:{Colors.ENDC}")
    print(f"{Colors.WARNING}• Ensure all dependencies are installed (ChromaDB, sentence-transformers, etc.){Colors.ENDC}")
    print(f"{Colors.WARNING}• Configure your LLM client properly{Colors.ENDC}")
    print(f"{Colors.WARNING}• Have some test data in your vector database for context retrieval{Colors.ENDC}")
    
    print(f"\n{Colors.OKCYAN}Press Ctrl+C at any time to stop the demo{Colors.ENDC}")
    print(f"{Colors.HEADER}{'🔄'*80}{Colors.ENDC}\n")

async def main():
    """Main demo function"""
    try:
        print_intro()
        
        # Wait for user to be ready
        input(f"{Colors.BOLD}Press Enter to start the pipeline visualization demo...{Colors.ENDC}")
        
        # Run the demo
        await demo_queries()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}🛑 Demo interrupted by user{Colors.ENDC}")
        print(f"{Colors.WARNING}Thank you for trying the pipeline visualization!{Colors.ENDC}")
    except Exception as e:
        print(f"\n\n{Colors.FAIL}❌ Demo error: {e}{Colors.ENDC}")
        print(f"{Colors.FAIL}Please check your configuration and dependencies{Colors.ENDC}")
    finally:
        print(f"\n{Colors.OKCYAN}Goodbye! 👋{Colors.ENDC}\n")

if __name__ == "__main__":
    asyncio.run(main())
