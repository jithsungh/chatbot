import time
from typing import List, Tuple, Optional, Dict, Any
from src.inference.ContextRetriever import SimpleContextRetriever
from src.inference.PipelineVisualizer import Colors

class EnhancedContextRetriever(SimpleContextRetriever):
    """
    Enhanced Context Retriever with detailed visualization and analysis.
    Extends the original SimpleContextRetriever with comprehensive logging and metrics.
    """
    
    def __init__(self, path: str = None, collection: str = None, embedding_model=None):
        super().__init__(path, collection, embedding_model)
        self.retrieval_count = 0
        self.retrieval_history = []
        print(f"{Colors.RETRIEVER}✅ Enhanced Context Retriever initialized{Colors.ENDC}")
    
    def retrieve_context_with_details(self, query: str, dept: str, k: int = 10) -> Dict[str, Any]:
        """
        Retrieve context with detailed analysis and visualization.
        """
        start_time = time.perf_counter()
        self.retrieval_count += 1
        
        print(f"{Colors.RETRIEVER}🔍 Context Retrieval #{self.retrieval_count}{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Query: \"{query[:60]}...\"{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Department: {dept}{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Requested chunks: {k}{Colors.ENDC}")
        
        try:
            # Initialize ChromaDB if needed
            init_start = time.perf_counter()
            if not self._initialize_chromadb():
                print(f"{Colors.FAIL}❌ ChromaDB initialization failed{Colors.ENDC}")
                return {
                    'chunks': [],
                    'search_time': 0.0,
                    'total_time': time.perf_counter() - start_time,
                    'error': 'ChromaDB initialization failed',
                    'filter_applied': None,
                    'model_used': None
                }
            init_time = time.perf_counter() - init_start
            
            # Get embedding model
            model_start = time.perf_counter()
            model = self._get_embedding_model()
            model_time = time.perf_counter() - model_start
            
            if model is None:
                print(f"{Colors.FAIL}❌ No embedding model available for similarity search{Colors.ENDC}")
                return {
                    'chunks': [],
                    'search_time': 0.0,
                    'total_time': time.perf_counter() - start_time,
                    'error': 'No embedding model available',
                    'filter_applied': None,
                    'model_used': None
                }
            
            # Apply department filter
            filter_dict = self._apply_department_filter(dept)
            print(f"{Colors.RETRIEVER}Filter applied: {filter_dict}{Colors.ENDC}")
            
            # Generate query embedding
            embedding_start = time.perf_counter()
            query_embedding = model.encode(query).tolist()
            embedding_time = time.perf_counter() - embedding_start
            
            print(f"{Colors.RETRIEVER}Query embedding generated in {embedding_time:.3f}s{Colors.ENDC}")
            
            # Perform search
            search_start = time.perf_counter()
            try:
                if filter_dict:
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=k,
                        where=filter_dict
                    )
                else:
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=k
                    )
                search_time = time.perf_counter() - search_start
                print(f"{Colors.RETRIEVER}Vector search completed in {search_time:.3f}s{Colors.ENDC}")
                
            except Exception as e:
                print(f"{Colors.FAIL}❌ Error during vector search: {e}{Colors.ENDC}")
                # Fallback: try without filter
                if filter_dict:
                    print(f"{Colors.WARNING}⚠️ Retrying search without department filter{Colors.ENDC}")
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=k
                    )
                    search_time = time.perf_counter() - search_start
                    filter_dict = None  # Mark that filter was removed
                else:
                    raise
            
            # Process results
            processing_start = time.perf_counter()
            chunks = []
            
            if results and 'documents' in results and 'distances' in results:
                documents = results['documents'][0] if results['documents'] else []
                distances = results['distances'][0] if results['distances'] else []
                metadatas = results.get('metadatas', [[]])[0] if results.get('metadatas') else []
                
                for i, (doc, distance) in enumerate(zip(documents, distances)):
                    similarity_score = 1 - distance  # Convert distance to similarity
                    chunks.append((doc, similarity_score))
                    
                    # Print chunk details for top 3
                    if i < 3:
                        metadata = metadatas[i] if i < len(metadatas) else {}
                        dept_info = metadata.get('department', 'Unknown')
                        print(f"{Colors.RETRIEVER}   Chunk {i+1}: Score={similarity_score:.4f}, Dept={dept_info}, Length={len(doc)}{Colors.ENDC}")
            
            processing_time = time.perf_counter() - processing_start
            total_time = time.perf_counter() - start_time
            
            # Calculate statistics
            total_chars = sum(len(chunk[0]) for chunk in chunks)
            avg_similarity = sum(chunk[1] for chunk in chunks) / len(chunks) if chunks else 0.0
            
            print(f"{Colors.RETRIEVER}📊 Retrieved {len(chunks)} chunks, {total_chars} total characters{Colors.ENDC}")
            print(f"{Colors.RETRIEVER}📊 Average similarity: {avg_similarity:.4f}{Colors.ENDC}")
            
            # Create detailed result
            result = {
                'chunks': chunks,
                'search_time': search_time,
                'total_time': total_time,
                'filter_applied': dept if filter_dict else None,
                'model_used': type(model).__name__,
                'timings': {
                    'init_time': init_time,
                    'model_time': model_time,
                    'embedding_time': embedding_time,
                    'search_time': search_time,
                    'processing_time': processing_time,
                    'total_time': total_time
                },
                'statistics': {
                    'chunks_found': len(chunks),
                    'total_characters': total_chars,
                    'average_similarity': avg_similarity,
                    'min_similarity': min(chunk[1] for chunk in chunks) if chunks else 0.0,
                    'max_similarity': max(chunk[1] for chunk in chunks) if chunks else 0.0
                },
                'retrieval_number': self.retrieval_count
            }
            
            # Store in history
            self.retrieval_history.append({
                'query': query[:100],
                'department': dept,
                'chunks_found': len(chunks),
                'total_time': total_time,
                'average_similarity': avg_similarity,
                'timestamp': time.time()
            })
            
            # Keep only last 100 retrievals
            if len(self.retrieval_history) > 100:
                self.retrieval_history.pop(0)
            
            print(f"{Colors.RETRIEVER}⚡ Context retrieval completed in {total_time:.3f}s{Colors.ENDC}")
            
            return result
            
        except Exception as e:
            total_time = time.perf_counter() - start_time
            print(f"{Colors.FAIL}❌ Error in enhanced context retrieval: {e}{Colors.ENDC}")
            
            return {
                'chunks': [],
                'search_time': 0.0,
                'total_time': total_time,
                'error': str(e),
                'filter_applied': dept if self._apply_department_filter(dept) else None,
                'model_used': None,
                'retrieval_number': self.retrieval_count
            }
    
    def get_retrieval_statistics(self) -> Dict[str, Any]:
        """Get comprehensive retrieval statistics"""
        if not self.retrieval_history:
            return {'message': 'No retrieval history available'}
        
        # Calculate various statistics
        total_retrievals = len(self.retrieval_history)
        avg_chunks = sum(entry['chunks_found'] for entry in self.retrieval_history) / total_retrievals
        avg_time = sum(entry['total_time'] for entry in self.retrieval_history) / total_retrievals
        avg_similarity = sum(entry['average_similarity'] for entry in self.retrieval_history) / total_retrievals
        
        # Department usage
        from collections import Counter
        dept_usage = Counter(entry['department'] for entry in self.retrieval_history)
        
        # Recent performance (last 10 retrievals)
        recent_retrievals = self.retrieval_history[-10:]
        recent_avg_time = sum(entry['total_time'] for entry in recent_retrievals) / len(recent_retrievals)
        recent_avg_chunks = sum(entry['chunks_found'] for entry in recent_retrievals) / len(recent_retrievals)
        
        return {
            'total_retrievals': total_retrievals,
            'average_chunks_per_query': avg_chunks,
            'average_retrieval_time': avg_time,
            'average_similarity_score': avg_similarity,
            'department_usage': dict(dept_usage),
            'recent_performance': {
                'average_time': recent_avg_time,
                'average_chunks': recent_avg_chunks
            }
        }
    
    def print_retrieval_statistics(self):
        """Print beautiful retrieval statistics"""
        stats = self.get_retrieval_statistics()
        
        if 'message' in stats:
            print(f"{Colors.RETRIEVER}{stats['message']}{Colors.ENDC}")
            return
        
        print(f"\n{Colors.RETRIEVER}📊 CONTEXT RETRIEVAL STATISTICS{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Total Retrievals: {stats['total_retrievals']}{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Average Chunks per Query: {stats['average_chunks_per_query']:.1f}{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Average Retrieval Time: {stats['average_retrieval_time']:.3f}s{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}Average Similarity Score: {stats['average_similarity_score']:.4f}{Colors.ENDC}")
        
        print(f"\n{Colors.RETRIEVER}Department Usage:{Colors.ENDC}")
        for dept, count in stats['department_usage'].items():
            percentage = (count / stats['total_retrievals']) * 100
            print(f"{Colors.RETRIEVER}  {dept}: {count} ({percentage:.1f}%){Colors.ENDC}")
        
        recent = stats['recent_performance']
        print(f"\n{Colors.RETRIEVER}Recent Performance (last 10):{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}  Average Time: {recent['average_time']:.3f}s{Colors.ENDC}")
        print(f"{Colors.RETRIEVER}  Average Chunks: {recent['average_chunks']:.1f}{Colors.ENDC}")
        
        print(f"{Colors.RETRIEVER}{'='*50}{Colors.ENDC}\n")
    
    # Keep original method for backward compatibility
    def retrieve_context(self, query: str, dept: str, k: int = 10) -> List[Tuple[str, float]]:
        """Original retrieve_context method for backward compatibility"""
        result = self.retrieve_context_with_details(query, dept, k)
        return result['chunks']
