from sentence_transformers import util
from typing import Dict, List
from sqlalchemy.orm import Session
from src.models.user_question import UserQuestion
from src.config import Config

def compute_similarity_matrix(embeddings):
    """
    Compute pairwise cosine similarity matrix
    
    Args:
        embeddings: Tensor of embeddings
        
    Returns:
        numpy array: Similarity matrix
    """
    # Compute cosine similarity matrix
    similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)
    return similarity_matrix.cpu().numpy()

def print_similarity_analysis(questions: List[dict], embeddings, similarity_matrix, threshold: float):
    """
    Print detailed similarity analysis for debugging
    
    Args:
        questions: List of question dictionaries
        embeddings: Question embeddings
        similarity_matrix: Pairwise similarity matrix
        threshold: Similarity threshold
    """
    print("\n" + "="*80)
    print("📊 DETAILED SIMILARITY ANALYSIS")
    print("="*80)
    
    n = len(questions)
    print(f"Number of questions: {n}")
    print(f"Similarity threshold: {threshold}")
    print(f"Embedding dimensions: {embeddings.shape[1]}")
    
    print("\n🔍 QUESTIONS:")
    for i, q in enumerate(questions):
        print(f"Q{i+1}: {q['query']}")
    
    print(f"\n📈 SIMILARITY MATRIX:")
    print("    ", end="")
    for i in range(n):
        print(f"Q{i+1:2}", end="   ")
    print()
    
    for i in range(n):
        print(f"Q{i+1:2}  ", end="")
        for j in range(n):
            score = similarity_matrix[i, j]
            if i == j:
                print("1.00", end="  ")
            else:
                color = "🟢" if score >= threshold else "🔴"
                print(f"{score:.2f}", end="  ")
        print()
    
    print(f"\n🎯 PAIRS ABOVE THRESHOLD ({threshold}):")
    pairs_found = False
    for i in range(n):
        for j in range(i + 1, n):
            score = similarity_matrix[i, j]
            if score >= threshold:
                pairs_found = True
                print(f"  Q{i+1} ↔ Q{j+1}: {score:.3f}")
                print(f"    '{questions[i]['query']}'")
                print(f"    '{questions[j]['query']}'")
                print()
    
    if not pairs_found:
        print("  ❌ No pairs found above threshold!")
        print("\n💡 HIGHEST SIMILARITIES:")
        # Find top 3 similarities (excluding self-similarities)
        similarities = []
        for i in range(n):
            for j in range(i + 1, n):
                similarities.append((i, j, similarity_matrix[i, j]))
        
        similarities.sort(key=lambda x: x[2], reverse=True)
        for i, (qi, qj, score) in enumerate(similarities[:3]):
            print(f"  #{i+1}: Q{qi+1} ↔ Q{qj+1}: {score:.3f}")

def manual_clustering(embeddings, similarity_matrix, threshold: float) -> List[List[int]]:
    """
    Manual clustering implementation with detailed logging
    
    Args:
        embeddings: Question embeddings
        similarity_matrix: Pairwise similarity matrix
        threshold: Similarity threshold
        
    Returns:
        List of clusters (each cluster is a list of indices)
    """
    n = len(embeddings)
    visited = [False] * n
    clusters = []
    
    print(f"\n🔗 MANUAL CLUSTERING (threshold: {threshold}):")
    
    for i in range(n):
        if visited[i]:
            continue
            
        # Start new cluster with question i
        cluster = [i]
        visited[i] = True
        
        # Find all questions similar to any question in current cluster
        changed = True
        while changed:
            changed = False
            for cluster_idx in cluster[:]:  # Copy to avoid modification during iteration
                for j in range(n):
                    if not visited[j] and similarity_matrix[cluster_idx, j] >= threshold:
                        cluster.append(j)
                        visited[j] = True
                        changed = True
                        print(f"  Added Q{j+1} to cluster (similar to Q{cluster_idx+1}: {similarity_matrix[cluster_idx, j]:.3f})")
        
        clusters.append(cluster)
        if len(cluster) > 1:
            print(f"  ✅ Cluster {len(clusters)}: {[f'Q{idx+1}' for idx in cluster]}")
        else:
            print(f"  🔸 Singleton: Q{cluster[0]+1}")
    
    return clusters

def fetch_and_deduplicate_pending_questions(
    session: Session,
    similarity_threshold: float = 0.4,
    debug_mode: bool = True
) -> Dict[str, List[List[dict]]]:
    """
    Fetch all pending questions from UserQuestion model, group by department,
    perform semantic deduplication, and cluster similar questions.

    Args:
        session: SQLAlchemy session
        similarity_threshold: Cosine similarity threshold (0-1) for clustering
        debug_mode: Whether to print detailed debugging information

    Returns:
        Dict where key = department, value = list of clusters
        Each cluster is a list of question dicts
    """
    try:
        # Step 1: Fetch pending questions grouped by department using the model
        grouped_questions = UserQuestion.fetch_pending_by_dept(session)

        if not grouped_questions:
            print("ℹ️ No pending questions found in database")
            return {}

        clustered_by_dept = {}

        # Step 2: For each department, perform semantic clustering
        for dept, qlist in grouped_questions.items():
            if not qlist:
                clustered_by_dept[dept] = []
                continue

            print(f"\n🏢 PROCESSING DEPARTMENT: {dept}")
            print(f"📝 Found {len(qlist)} questions")
            
            texts = [q["query"] for q in qlist]

            # Step 2a: Compute embeddings
            print("🧠 Computing embeddings...")
            model = Config.get_embedding_model_deputy()
            embeddings = model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)
            print(f"   Embedding shape: {embeddings.shape}")

            # Step 2b: Compute similarity matrix
            print("📊 Computing similarity matrix...")
            similarity_matrix = compute_similarity_matrix(embeddings)
            
            if debug_mode:
                print_similarity_analysis(qlist, embeddings, similarity_matrix, similarity_threshold)

            # Step 2c: Try both community detection and manual clustering
            print(f"\n🔗 CLUSTERING METHODS COMPARISON:")
            
            # Method 1: Community detection (original)
            try:
                print("\n1️⃣ Community Detection Method:")
                communities = util.community_detection(
                    embeddings,
                    min_community_size=1,
                    threshold=similarity_threshold
                )
                print(f"   Found {len(communities)} communities")
                for i, community in enumerate(communities):
                    if len(community) > 1:
                        print(f"   Community {i+1}: {[f'Q{idx+1}' for idx in community]}")
                    else:
                        print(f"   Singleton: Q{community[0]+1}")
                
                # Use community detection results
                clustered_questions = []
                for cluster_indices in communities:
                    clustered_questions.append([qlist[i] for i in cluster_indices])
                    
            except Exception as e:
                print(f"   ❌ Community detection failed: {e}")
                print("\n2️⃣ Fallback to Manual Clustering:")
                
                # Method 2: Manual clustering (fallback)
                manual_clusters = manual_clustering(embeddings, similarity_matrix, similarity_threshold)
                clustered_questions = []
                for cluster_indices in manual_clusters:
                    clustered_questions.append([qlist[i] for i in cluster_indices])

            clustered_by_dept[dept] = clustered_questions
            
            # Summary
            print(f"\n✅ FINAL RESULT for {dept}:")
            print(f"   Input: {len(qlist)} questions")
            print(f"   Output: {len(clustered_questions)} clusters")
            
            multi_question_clusters = [c for c in clustered_questions if len(c) > 1]
            if multi_question_clusters:
                print(f"   Merged clusters: {len(multi_question_clusters)}")
                for i, cluster in enumerate(multi_question_clusters):
                    print(f"     Cluster {i+1}: {len(cluster)} questions")
                    for q in cluster:
                        print(f"       - {q['query']}")
            else:
                print("   ⚠️ No questions were clustered together!")
                print("   💡 Consider lowering the similarity threshold")

        return clustered_by_dept
    
    except Exception as e:
        print(f"❌ Error in fetch_and_deduplicate_pending_questions: {e}")
        import traceback
        traceback.print_exc()
        raise

def test_similarity_threshold():
    """
    Test function to help determine optimal similarity threshold
    """
    print("🧪 SIMILARITY THRESHOLD TESTING")
    print("="*50)
    
    # Sample similar questions for testing
    test_questions = [
        "How do I reset my password?",
        "How to reset password?", 
        "Password reset procedure?",
        "I forgot my password",
        "How do I request a laptop?",
        "Laptop request process?",
        "What is the leave policy?",
        "How many leaves do I get?"
    ]
    
    print("Test questions:")
    for i, q in enumerate(test_questions):
        print(f"  Q{i+1}: {q}")
    
    model = Config.get_embedding_model_deputy()
    # Compute embeddings and similarities
    embeddings = model.encode(test_questions, convert_to_tensor=True, normalize_embeddings=True)
    similarity_matrix = compute_similarity_matrix(embeddings)
    
    # Show similarity matrix for reference
    print("\n📈 SIMILARITY MATRIX:")
    print("     ", end="")
    for i in range(len(test_questions)):
        print(f"Q{i+1:2}", end="  ")
    print()
    
    for i in range(len(test_questions)):
        print(f"Q{i+1:2}  ", end="")
        for j in range(len(test_questions)):
            score = similarity_matrix[i, j]
            if i == j:
                print("1.00", end=" ")
            else:
                print(f"{score:.2f}", end=" ")
        print()
    
    # Test different thresholds
    thresholds = [0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
    
    for threshold in thresholds:
        print(f"\n📊 Threshold: {threshold}")
        print("-" * 40)
        
        communities = util.community_detection(
            embeddings,
            min_community_size=1,
            threshold=threshold
        )
        
        print(f"   Total clusters: {len(communities)}")
        
        # Separate multi-question clusters from singletons
        multi_clusters = []
        singletons = []
        
        for i, community in enumerate(communities):
            if len(community) > 1:
                questions_in_cluster = [test_questions[idx] for idx in community]
                multi_clusters.append((i+1, community, questions_in_cluster))
            else:
                singletons.extend([test_questions[idx] for idx in community])
        
        # Display multi-question clusters
        if multi_clusters:
            print(f"   Multi-question clusters: {len(multi_clusters)}")
            for cluster_num, indices, questions in multi_clusters:
                print(f"     Cluster {cluster_num} ({len(questions)} questions):")
                for q in questions:
                    print(f"       - {q}")
        else:
            print("   Multi-question clusters: 0")
        
        # Display singletons
        if singletons:
            print(f"   Singleton questions: {len(singletons)}")
            for q in singletons:
                print(f"     - {q}")
        else:
            print("   Singleton questions: 0")
        
        # Account for all questions
        total_questions_in_clusters = sum(len(community) for community in communities)
        print(f"   ✅ Total questions accounted for: {total_questions_in_clusters}/{len(test_questions)}")

def test_real_questions():
    """
    Test clustering with real questions from your database
    """
    print("\n🏢 REAL DATABASE QUESTIONS TEST")
    print("="*50)
    
    try:
        from src.config import Config
        session = Config.get_session()
        
        # Fetch real pending questions
        grouped_questions = UserQuestion.fetch_pending_by_dept(session)
        
        if not grouped_questions:
            print("❌ No pending questions found in database")
            return
        
        print(f"📊 Found {len(grouped_questions)} departments with questions")
        
        for dept, questions in grouped_questions.items():
            if not questions:
                continue
                
            print(f"\n🏢 Department: {dept}")
            print(f"📝 Questions ({len(questions)}):")
            
            # Debug: Check the structure of questions
            if questions:
                print(f"   🔍 Sample question structure: {type(questions[0])}")
                if isinstance(questions[0], dict):
                    print(f"   🔍 Keys: {list(questions[0].keys())}")
            
            # Extract queries safely
            queries = []
            for i, q in enumerate(questions):
                try:
                    if isinstance(q, dict):
                        query_text = q.get('query', str(q))
                    else:
                        query_text = str(q)
                    queries.append(query_text)
                    print(f"  Q{i+1}: {query_text}")
                except Exception as e:
                    print(f"  ⚠️ Error processing question {i+1}: {e}")
                    continue
            
            if len(queries) < 2:
                print("  ⚠️ Not enough valid questions for clustering analysis")
                continue
            
            # Test clustering with different thresholds
            try:
                model = Config.get_embedding_model_deputy()
                embeddings = model.encode(queries, convert_to_tensor=True, normalize_embeddings=True)
                similarity_matrix = compute_similarity_matrix(embeddings)
                
                print(f"\n📈 Similarity Analysis for {dept}:")
                
                # Create question dicts for analysis if needed
                question_dicts = []
                for i, query in enumerate(queries):
                    if isinstance(questions[i], dict):
                        question_dicts.append(questions[i])
                    else:
                        question_dicts.append({'query': query, 'id': i})
                
                print_similarity_analysis(question_dicts, embeddings, similarity_matrix, 0.75)
                
                # Test multiple thresholds
                print(f"\n🔬 Threshold Testing for {dept}:")
                for threshold in [0.4, 0.5, 0.6, 0.7, 0.75, 0.8]:
                    print(f"\n📊 Threshold: {threshold}")
                    print("-" * 40)
                    
                    try:
                        communities = util.community_detection(
                            embeddings,
                            min_community_size=1,
                            threshold=threshold
                        )
                        
                        print(f"   Total clusters: {len(communities)}")
                        
                        # Separate multi-question clusters from singletons
                        multi_clusters = []
                        singletons = []
                        
                        for i, community in enumerate(communities):
                            if len(community) > 1:
                                questions_in_cluster = [queries[idx] for idx in community]
                                multi_clusters.append((i+1, community, questions_in_cluster))
                            else:
                                singletons.extend([queries[idx] for idx in community])
                        
                        # Display multi-question clusters
                        if multi_clusters:
                            print(f"   Multi-question clusters: {len(multi_clusters)}")
                            for cluster_num, indices, cluster_questions in multi_clusters:
                                print(f"     Cluster {cluster_num} ({len(cluster_questions)} questions):")
                                for q_text in cluster_questions:
                                    print(f"       - {q_text}")
                        else:
                            print("   Multi-question clusters: 0")
                        
                        # Display singletons
                        if singletons:
                            print(f"   Singleton questions: {len(singletons)}")
                            for q_text in singletons:
                                print(f"     - {q_text}")
                        else:
                            print("   Singleton questions: 0")
                        
                        # Account for all questions
                        total_questions_in_clusters = sum(len(community) for community in communities)
                        print(f"   ✅ Total questions accounted for: {total_questions_in_clusters}/{len(queries)}")
                        
                    except Exception as e:
                        print(f"   ❌ Error in community detection for threshold {threshold}: {e}")
                        continue
                        
            except Exception as e:
                print(f"   ❌ Error in similarity analysis for {dept}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error testing real questions: {e}")
        import traceback
        traceback.print_exc()

# if __name__ == "__main__":
#     # Run threshold testing with sample questions
#     test_similarity_threshold()
    
#     # Test with real database questions
#     test_real_questions()