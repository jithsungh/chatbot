from collections import Counter
import re
import time
from typing import Dict, List, Optional, Any
from src.inference.HybridRouter import HybridDepartmentRouter
from src.inference.PipelineVisualizer import Colors

class EnhancedDepartmentRouter(HybridDepartmentRouter):
    """
    Enhanced Department Router with detailed visualization and analysis.
    Extends the original HybridDepartmentRouter with comprehensive logging and metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.query_count = 0
        self.routing_history = []
        print(f"{Colors.ROUTER}✅ Enhanced Department Router initialized{Colors.ENDC}")
    
    def route_query_with_details(self, query: str) -> Dict[str, Any]:
        """
        Route query and return detailed analysis information.
        """
        start_time = time.perf_counter()
        self.query_count += 1
        
        try:
            # Clean and normalize query
            query_clean = query.lower().strip()
            
            print(f"{Colors.ROUTER}🔍 Analyzing query: \"{query[:50]}...\"{Colors.ENDC}")
            print(f"{Colors.ROUTER}📊 Query #{self.query_count} | Length: {len(query)} chars{Colors.ENDC}")
            
            # Method 1: Keyword-based routing (fast and reliable)
            keyword_start = time.perf_counter()
            keyword_result = self._route_by_keywords_detailed(query_clean)
            keyword_time = time.perf_counter() - keyword_start
            
            # Method 2: Embedding-based routing (if available)
            embedding_start = time.perf_counter()
            embedding_result = self._route_by_embeddings_detailed(query) if self._get_model() else None
            embedding_time = time.perf_counter() - embedding_start
            
            # Determine final department with priority logic
            final_dept = None
            routing_method = None
            confidence = 0.0
            
            if keyword_result['department'] and keyword_result['department'] != "General Inquiry":
                final_dept = keyword_result['department']
                routing_method = "keyword"
                confidence = keyword_result['confidence']
                print(f"{Colors.ROUTER}🎯 Keyword routing selected: {final_dept} (confidence: {confidence:.3f}){Colors.ENDC}")
            elif embedding_result and embedding_result['department'] and embedding_result['department'] != "General Inquiry":
                final_dept = embedding_result['department']
                routing_method = "embedding"
                confidence = embedding_result['confidence']
                print(f"{Colors.ROUTER}🎯 Embedding routing selected: {final_dept} (confidence: {confidence:.3f}){Colors.ENDC}")
            else:
                final_dept = "General Inquiry"
                routing_method = "fallback"
                confidence = 0.1
                print(f"{Colors.ROUTER}🎯 Fallback to General Inquiry{Colors.ENDC}")
            
            total_time = time.perf_counter() - start_time
            
            # Create detailed result
            result = {
                'department': final_dept,
                'method': routing_method,
                'confidence': confidence,
                'query_clean': query_clean,
                'timings': {
                    'keyword_time': keyword_time,
                    'embedding_time': embedding_time,
                    'total_time': total_time
                },
                'keyword_analysis': keyword_result,
                'embedding_analysis': embedding_result,
                'query_number': self.query_count
            }
            
            # Store in history for analysis
            self.routing_history.append({
                'query': query[:100],
                'department': final_dept,
                'method': routing_method,
                'confidence': confidence,
                'timestamp': time.time()
            })
            
            # Keep only last 100 routing decisions
            if len(self.routing_history) > 100:
                self.routing_history.pop(0)
            
            print(f"{Colors.ROUTER}⚡ Routing completed in {total_time:.3f}s{Colors.ENDC}")
            
            return result
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error in enhanced route_query: {e}{Colors.ENDC}")
            return {
                'department': "General Inquiry",
                'method': "error_fallback",
                'confidence': 0.0,
                'error': str(e),
                'query_number': self.query_count
            }
    
    def _route_by_keywords_detailed(self, query_clean: str) -> Dict[str, Any]:
        """Enhanced keyword routing with detailed analysis"""
        try:
            print(f"{Colors.ROUTER}🔑 Starting keyword analysis...{Colors.ENDC}")
            
            scores = {}
            matched_keywords = {}
            
            for dept, keywords in self.keywords.items():
                score = 0
                matches = []
                words_in_query = query_clean.split()
                
                for keyword in keywords:
                    # Exact match
                    if keyword in query_clean:
                        score += 2
                        matches.append(f"{keyword} (exact)")
                    
                    # Word boundary match
                    elif any(keyword in word for word in words_in_query):
                        score += 1
                        matches.append(f"{keyword} (partial)")
                
                # Normalize by query length
                normalized_score = score / max(len(words_in_query), 1)
                scores[dept] = normalized_score
                matched_keywords[dept] = matches
                
                if matches:
                    print(f"{Colors.ROUTER}   {dept}: {normalized_score:.3f} ({len(matches)} matches){Colors.ENDC}")
            
            # Find department with highest score
            best_dept = "General Inquiry"
            best_score = 0.0
            
            if scores:
                best_dept_candidate = max(scores, key=scores.get)
                best_score_candidate = scores[best_dept_candidate]
                
                # Threshold for confidence
                if best_score_candidate > 0.1:  # Adjust threshold as needed
                    best_dept = best_dept_candidate
                    best_score = best_score_candidate
            
            return {
                'department': best_dept,
                'confidence': best_score,
                'all_scores': scores,
                'matched_keywords': matched_keywords[best_dept] if best_dept in matched_keywords else [],
                'threshold_met': best_score > 0.1
            }
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error in detailed keyword routing: {e}{Colors.ENDC}")
            return {
                'department': "General Inquiry",
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _route_by_embeddings_detailed(self, query: str) -> Optional[Dict[str, Any]]:
        """Enhanced embedding routing with detailed analysis"""
        try:
            print(f"{Colors.ROUTER}🧠 Starting embedding analysis...{Colors.ENDC}")
            
            model = self._get_model()
            department_embeddings = self._get_department_embeddings()
            
            if not model or not department_embeddings:
                print(f"{Colors.WARNING}⚠️ Embedding model or department embeddings not available{Colors.ENDC}")
                return None
            
            # Import util here
            from sentence_transformers import util
            
            # Get query embedding
            embedding_start = time.perf_counter()
            query_embedding = model.encode(query, convert_to_tensor=True)
            embedding_time = time.perf_counter() - embedding_start
            
            # Calculate similarities
            similarities = {}
            for dept, dept_embedding in department_embeddings.items():
                similarity = util.pytorch_cos_sim(query_embedding, dept_embedding)[0][0].item()
                similarities[dept] = similarity
                print(f"{Colors.ROUTER}   {dept}: {similarity:.4f} similarity{Colors.ENDC}")
            
            # Find best match
            best_dept = "General Inquiry"
            best_similarity = 0.0
            
            if similarities:
                best_dept_candidate = max(similarities, key=similarities.get)
                best_similarity_candidate = similarities[best_dept_candidate]
                
                # Threshold for confidence (adjust as needed)
                if best_similarity_candidate > 0.3:
                    best_dept = best_dept_candidate
                    best_similarity = best_similarity_candidate
            
            return {
                'department': best_dept,
                'confidence': best_similarity,
                'all_similarities': similarities,
                'embedding_time': embedding_time,
                'threshold_met': best_similarity > 0.3,
                'model_used': type(model).__name__
            }
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error in detailed embedding routing: {e}{Colors.ENDC}")
            return {
                'department': "General Inquiry",
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics"""
        if not self.routing_history:
            return {'message': 'No routing history available'}
        
        # Department distribution
        dept_counts = Counter(entry['department'] for entry in self.routing_history)
        
        # Method distribution  
        method_counts = Counter(entry['method'] for entry in self.routing_history)
        
        # Average confidence by department
        dept_confidence = {}
        for dept in dept_counts.keys():
            confidences = [entry['confidence'] for entry in self.routing_history if entry['department'] == dept]
            dept_confidence[dept] = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Recent performance (last 10 queries)
        recent_queries = self.routing_history[-10:]
        recent_avg_confidence = sum(entry['confidence'] for entry in recent_queries) / len(recent_queries)
        
        return {
            'total_queries': len(self.routing_history),
            'department_distribution': dict(dept_counts),
            'method_distribution': dict(method_counts),
            'average_confidence_by_department': dept_confidence,
            'recent_average_confidence': recent_avg_confidence,
            'loaded_departments': len(self.department_descriptions),
            'total_keywords': sum(len(kws) for kws in self.keywords.values())
        }
    
    def print_routing_statistics(self):
        """Print beautiful routing statistics"""
        stats = self.get_routing_statistics()
        
        print(f"\n{Colors.ROUTER}📊 ROUTING STATISTICS{Colors.ENDC}")
        print(f"{Colors.ROUTER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.ROUTER}Total Queries Processed: {stats['total_queries']}{Colors.ENDC}")
        
        print(f"\n{Colors.ROUTER}Department Distribution:{Colors.ENDC}")
        for dept, count in stats['department_distribution'].items():
            percentage = (count / stats['total_queries']) * 100
            print(f"{Colors.ROUTER}  {dept}: {count} ({percentage:.1f}%){Colors.ENDC}")
        
        print(f"\n{Colors.ROUTER}Routing Method Distribution:{Colors.ENDC}")
        for method, count in stats['method_distribution'].items():
            percentage = (count / stats['total_queries']) * 100
            print(f"{Colors.ROUTER}  {method}: {count} ({percentage:.1f}%){Colors.ENDC}")
        
        print(f"\n{Colors.ROUTER}Average Confidence by Department:{Colors.ENDC}")
        for dept, confidence in stats['average_confidence_by_department'].items():
            print(f"{Colors.ROUTER}  {dept}: {confidence:.3f}{Colors.ENDC}")
        
        print(f"\n{Colors.ROUTER}Recent Performance: {stats['recent_average_confidence']:.3f}{Colors.ENDC}")
        print(f"{Colors.ROUTER}{'='*50}{Colors.ENDC}\n")
    
    # Keep original route_query method for backward compatibility
    def route_query(self, query: str) -> str:
        """Original route_query method for backward compatibility"""
        result = self.route_query_with_details(query)
        return result['department']
