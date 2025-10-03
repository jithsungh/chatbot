"""
Dataset Generation Script for Q&A Pairs

This script:
1. Retrieves all documents from ChromaDB collection 'TM-DOCS'
2. Generates 5-7 question-answer pairs for each document using OpenAI LLM
3. Handles rate limiting (30 requests/minute) with proper sleep intervals
4. Provides comprehensive logging of progress and operations
5. Appends results to qa.jsonl in the required format

Output format:
{
  "instruction": "How many paid leave days do employees get?",
  "input": "<Context related to that question (document text)>",
  "output": "Employees are entitled to 20 days of paid leave per year."
}
"""

import json
import time
import logging
from typing import List, Dict, Any
import chromadb
from datetime import datetime
import os

from src.utils.LLMClientGemma import LLMClientGemma
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dataset_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatasetGenerator:
    def __init__(self):
        """Initialize the dataset generator with ChromaDB and LLM client"""
        self.chromadb_path = Config.CHROMADB_PATH
        self.collection_name = Config.COLLECTION_NAME
        self.output_file = "qa.jsonl"
        self.rate_limit_delay = 4.0  # 4.0 seconds between requests (15 req/min, safer buffer)
        
        # Initialize ChromaDB
        try:
            self.client = chromadb.PersistentClient(path=self.chromadb_path)
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"✅ Connected to ChromaDB collection: {self.collection_name}")
            logger.info(f"📊 Collection contains {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"❌ Failed to connect to ChromaDB: {e}")
            raise
          # Initialize LLM client
        try:
            self.llm_client = LLMClientGemma()
            logger.info("✅ LLM client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            raise
        
        self.processed_count = 0
        self.total_qa_pairs = 0
        self.failed_generations = 0

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retrieve all documents from the ChromaDB collection"""
        try:
            logger.info("🔍 Retrieving all documents from ChromaDB...")
            
            # Get total count first
            total_count = self.collection.count()
            logger.info(f"📊 Total documents in collection: {total_count}")
            
            if total_count == 0:
                logger.warning("⚠️ No documents found in collection")
                return []
              # Retrieve all documents with their content and metadata
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            documents = []
            for i, (doc_id, content, metadata) in enumerate(zip(
                results["ids"],
                results["documents"], 
                results["metadatas"]
            )):
                documents.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata or {}
                })
                
                if (i + 1) % 100 == 0:  # Log progress every 100 documents
                    logger.info(f"📥 Retrieved {i + 1}/{total_count} documents")
            
            logger.info(f"✅ Successfully retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve documents: {e}")
            raise

    def generate_qa_prompt(self, document_content: str, document_metadata: Dict) -> str:
        """Generate a prompt for creating Q&A pairs from document content"""
        
        department = document_metadata.get("department", "General")
        title = document_metadata.get("title", "Document")
        
        prompt = f"""You are an expert at creating high-quality question-answer pairs for training datasets. 

Given the following document content from the {department} department titled "{title}", generate exactly 5-7 diverse question-answer pairs that cover different aspects of the content.

Document Content:
{document_content}

Requirements:
1. Create exactly 5-7 question-answer pairs
2. Questions should be natural and varied (what, how, when, why, who, etc.)
3. Answers should be comprehensive but concise
4. Cover different topics/aspects from the document
5. Questions should be specific to the content provided
6. Answers must be directly answerable from the given content

Format your response as a JSON array with this exact structure:
[
  {{
    "instruction": "Your question here?",
    "input": "Relevant excerpt from document content",
    "output": "Complete answer based on the document"
  }},
  {{
    "instruction": "Another question?",
    "input": "Another relevant excerpt from document content", 
    "output": "Another complete answer"
  }}
]

Important: Respond ONLY with the JSON array, no additional text or formatting."""

        return prompt

    def parse_llm_response(self, response_text) -> List[Dict[str, str]]:
        """Parse the LLM response and extract Q&A pairs"""
        try:
            # Handle different response formats
            cleaned_response = ""
            if hasattr(response_text, 'content'):
                cleaned_response = response_text.content.strip()
            elif hasattr(response_text, 'text'):
                cleaned_response = response_text.text.strip()
            elif isinstance(response_text, str):
                cleaned_response = response_text.strip()
            else:
                # For AIMessage or other objects, try to get string representation
                cleaned_response = str(response_text).strip()
            
            # Try to find JSON array in the response
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                logger.error("❌ No JSON array found in LLM response")
                logger.error(f"🔍 Raw response (first 500 chars): {cleaned_response[:500]}")
                return []
            
            json_str = cleaned_response[start_idx:end_idx]
            qa_pairs = json.loads(json_str)
            
            # Validate the structure
            valid_pairs = []
            for pair in qa_pairs:
                if (isinstance(pair, dict) and 
                    "instruction" in pair and 
                    "input" in pair and 
                    "output" in pair):
                    valid_pairs.append(pair)
                else:
                    logger.warning("⚠️ Invalid Q&A pair structure found, skipping")
            
            return valid_pairs
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from LLM response: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing LLM response: {e}")
            return []

    def generate_qa_pairs_for_document(self, document: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate Q&A pairs for a single document"""
        try:
            doc_id = document["id"]
            content = document["content"]
            metadata = document["metadata"]
            
            logger.info(f"🔄 Generating Q&A pairs for document: {doc_id}")
            logger.info(f"📝 Content length: {len(content)} characters")
            logger.info(f"🏢 Department: {metadata.get('department', 'Unknown')}")
            
            # Skip if content is too short
            if len(content.strip()) < 50:
                logger.warning(f"⚠️ Skipping document {doc_id} - content too short")
                return []
            
            # Generate prompt
            prompt = self.generate_qa_prompt(content, metadata)
            
            # Apply rate limiting
            logger.info(f"⏳ Applying rate limit delay: {self.rate_limit_delay} seconds")
            time.sleep(self.rate_limit_delay)
            
            # Get response from LLM
            logger.info("🤖 Requesting Q&A generation from LLM...")
            start_time = time.time()
            response = self.llm_client.get_response(prompt)
            end_time = time.time()
            
            logger.info(f"✅ LLM response received in {end_time - start_time:.2f} seconds")
            
            # Parse the response
            qa_pairs = self.parse_llm_response(response)
            
            if qa_pairs:
                logger.info(f"✅ Generated {len(qa_pairs)} Q&A pairs for document {doc_id}")
                return qa_pairs
            else:
                logger.error(f"❌ Failed to generate valid Q&A pairs for document {doc_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error generating Q&A pairs for document {document['id']}: {e}")
            return []

    def save_qa_pairs(self, qa_pairs: List[Dict[str, str]]) -> bool:
        """Save Q&A pairs to the JSONL file"""
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                for pair in qa_pairs:
                    json_line = json.dumps(pair, ensure_ascii=False)
                    f.write(json_line + "\n")
            
            logger.info(f"💾 Saved {len(qa_pairs)} Q&A pairs to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save Q&A pairs: {e}")
            return False

    def generate_dataset(self):
        """Main method to generate the complete dataset"""
        logger.info("🚀 Starting dataset generation process")
        logger.info(f"📂 ChromaDB path: {self.chromadb_path}")
        logger.info(f"📊 Collection name: {self.collection_name}")
        logger.info(f"💾 Output file: {self.output_file}")
        logger.info(f"⏱️ Rate limit delay: {self.rate_limit_delay} seconds")
        
        start_time = datetime.now()
        
        try:
            # Get all documents
            documents = self.get_all_documents()
            total_documents = len(documents)
            
            if total_documents == 0:
                logger.error("❌ No documents to process. Exiting.")
                return
            
            logger.info(f"📋 Processing {total_documents} documents...")
            
            # Process each document
            for idx, document in enumerate(documents, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"📄 Processing document {idx}/{total_documents}")
                logger.info(f"🆔 Document ID: {document['id']}")
                logger.info(f"{'='*60}")
                
                # Generate Q&A pairs
                qa_pairs = self.generate_qa_pairs_for_document(document)
                
                if qa_pairs:
                    # Save to file
                    if self.save_qa_pairs(qa_pairs):
                        self.total_qa_pairs += len(qa_pairs)
                        self.processed_count += 1
                        logger.info(f"✅ Document {idx} processed successfully")
                    else:
                        self.failed_generations += 1
                        logger.error(f"❌ Failed to save Q&A pairs for document {idx}")
                else:
                    self.failed_generations += 1
                    logger.error(f"❌ No Q&A pairs generated for document {idx}")
                
                # Progress update
                progress = (idx / total_documents) * 100
                logger.info(f"📊 Progress: {progress:.1f}% ({idx}/{total_documents})")
                logger.info(f"📈 Total Q&A pairs generated so far: {self.total_qa_pairs}")
                
                # Estimated time remaining
                if idx > 0:
                    elapsed = datetime.now() - start_time
                    avg_time_per_doc = elapsed.total_seconds() / idx
                    remaining_docs = total_documents - idx
                    eta_seconds = remaining_docs * avg_time_per_doc
                    eta_minutes = eta_seconds / 60
                    logger.info(f"⏰ Estimated time remaining: {eta_minutes:.1f} minutes")
        
        except KeyboardInterrupt:
            logger.warning("⚠️ Process interrupted by user")
        except Exception as e:
            logger.error(f"❌ Fatal error in dataset generation: {e}")
        finally:
            # Final statistics
            end_time = datetime.now()
            total_time = end_time - start_time
            
            logger.info(f"\n{'='*60}")
            logger.info("📊 FINAL STATISTICS")
            logger.info(f"{'='*60}")
            logger.info(f"⏰ Total processing time: {total_time}")
            logger.info(f"📄 Documents processed: {self.processed_count}")
            logger.info(f"❌ Failed generations: {self.failed_generations}")
            logger.info(f"📝 Total Q&A pairs generated: {self.total_qa_pairs}")
            logger.info(f"💾 Output saved to: {self.output_file}")
            
            if self.processed_count > 0:
                avg_pairs_per_doc = self.total_qa_pairs / self.processed_count
                logger.info(f"📊 Average Q&A pairs per document: {avg_pairs_per_doc:.1f}")
            
            logger.info("🏁 Dataset generation completed!")


def main():
    """Main function to run the dataset generation"""
    try:
        generator = DatasetGenerator()
        generator.generate_dataset()
    except Exception as e:
        logger.error(f"❌ Failed to initialize dataset generator: {e}")
        raise


if __name__ == "__main__":
    main()
