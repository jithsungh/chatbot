from typing import List, Dict
from src.utils.LLMClientOpenAI import LLMClientOpenAI
from src.config import Config

class QuestionSummarizer:
    def __init__(self):
        """
        Initialize QuestionSummarizer with LLM client.
        """
        try:
            self.llm_client = LLMClientOpenAI()
        except Exception as e:
            print(f"❌ Failed to initialize LLM client: {e}")
            raise

    @staticmethod
    def generate_prompt(cluster: List[Dict]) -> str:
        """
        Generate a prompt for the LLM to merge similar questions into a single representative question.

        Args:
            cluster: List of question dicts, each dict must have 'query' key.

        Returns:
            str: Prompt string ready to pass to LLM
        """
        if not cluster:
            raise ValueError("Cluster cannot be empty")
        
        # Extract the raw queries
        queries = [q.get("query", "") for q in cluster if q.get("query")]
        
        if not queries:
            raise ValueError("No valid queries found in cluster")
            
        queries_text = "\n".join([f"- {q}" for q in queries])

        # Prompt template
        prompt = f"""
            You are an AI assistant at {Config.ORGANIZATION}, tasked with helping admins answer user questions efficiently.

            The following is a cluster of similar user questions that need to be merged into a single clear and concise representative question.

            User Questions Cluster:
            {queries_text}

            Instructions:
            1. Merge these questions into a single, comprehensive, and easy-to-understand question.
            2. Remove duplicates, redundant phrases, and reword for clarity.
            3. Keep the meaning intact and preserve the intent of the users.
            4. Return ONLY a valid JSON object with the following format:

            {{
                "representative_question": "<your merged question here>",
                "acceptance_criteria": "Acceptance criteria or suggestion for the answer, what to include or focus on",
                "original_questions": [{', '.join([f'"{q}"' for q in queries])}]
            }}

            Do not add any explanations or extra text. Return only JSON.
            """

        return prompt.strip()

    def summarize_clusters(self, clusters_by_dept: Dict[str, List[List[Dict]]]) -> Dict[str, List[str]]:
        """
        Summarize all clusters per department using the LLM.

        Args:
            clusters_by_dept: Dict[department, list of clusters], each cluster is a list of question dicts

        Returns:
            Dict[department, list of JSON strings], each JSON string contains representative_question and original_questions
        """
        if not clusters_by_dept:
            print("INFO: No clusters to summarize")
            return {}
            
        summarized_by_dept = {}

        for dept, clusters in clusters_by_dept.items():
            if not clusters:
                summarized_by_dept[dept] = []
                continue
                
            print(f"🤖 Summarizing {len(clusters)} clusters for department: {dept}")
            summarized_clusters = []

            for i, cluster in enumerate(clusters):
                if not cluster:
                    print(f"⚠️ Empty cluster {i+1} for dept {dept}, skipping")
                    continue
                    
                try:
                    print(f"✅ Summarized cluster {i+1}/{len(clusters)} for {dept}")
                    for i,q in enumerate(cluster):
                        print(f"  Q{i+1}: {q.get('query','')}")
                    # Generate prompt
                    prompt = self.generate_prompt(cluster)

                    # Call LLM
                    response = self.llm_client.get_response(prompt)

                    # Append JSON string
                    summarized_clusters.append(response.content)
                    print(f"✅ Summarized cluster {i+1}/{len(clusters)} for {dept}")
                    print("\n"+"="*60)
                    
                except Exception as e:
                    print(f"❌ Failed to summarize cluster {i+1} for dept {dept}: {e}")
                    # Create a fallback summary
                    queries = [q.get("query", "") for q in cluster if q.get("query")]
                    fallback_summary = f'{{"representative_question": "{queries[0] if queries else "Unknown question"}", "original_questions": {queries}}}'
                    summarized_clusters.append(fallback_summary)

            summarized_by_dept[dept] = summarized_clusters

        return summarized_by_dept

# Test function
def main():
    # Simulate 4 pending questions per department
    dummy_questions = {
        "HR": [
            {"query": "How can I apply for leave?"},
            {"query": "Leave application process?"},
            {"query": "Can I submit leave request online?"},
            {"query": "What is the HR leave policy?"}
        ],
        "IT": [
            {"query": "How to reset my email password?"},
            {"query": "I forgot my email password, how to reset?"},
            {"query": "Steps to change email password"},
            {"query": "Email password recovery process"}
        ],
        "Security": [
            {"query": "How to request building access?"},
            {"query": "What is the process for office entry?"},
            {"query": "Building access request procedure?"},
            {"query": "How do I get security clearance?"}
        ]
    }

    # Transform into clusters (for testing, we can treat each department as one cluster)
    clusters_by_dept = {dept: [questions] for dept, questions in dummy_questions.items()}

    try:
        # Initialize summarizer
        summarizer = QuestionSummarizer()

        # Generate summarized representative questions
        summarized_json = summarizer.summarize_clusters(clusters_by_dept)

        # Print results
        for dept, summaries in summarized_json.items():
            print(f"\nDepartment: {dept}")
            for i, summary in enumerate(summaries, 1):
                print(f" Cluster {i}: {summary}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()