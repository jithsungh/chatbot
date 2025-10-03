"""
QA Dataset Expansion Script

This script:
1. Reads each JSON entry from qa.jsonl
2. Creates 2-3 variations of each Q&A pair using different approaches:
   - Original format
   - Rephrased question format
   - Context-focused format
   - Direct answer format (optional)
3. Saves all variations to expanded_qa.jsonl
4. Provides comprehensive logging and statistics
"""

import json
import time
import logging
from typing import List, Dict, Any
from datetime import datetime
import os
import re

from src.utils.LLMClientGemma import LLMClientGemma
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qa_expansion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QADatasetExpander:
    def __init__(self):
        """Initialize the QA dataset expander"""
        self.input_file = "qa.jsonl"
        self.output_file = "expanded_qa.jsonl"
        self.rate_limit_delay = 3.0  # 3 seconds between LLM requests (20 req/min)
        
        # Initialize LLM client for rephrasing
        try:
            self.llm_client = LLMClientGemma()
            logger.info("✅ LLM client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            raise
        
        self.processed_count = 0
        self.total_variations = 0
        self.failed_expansions = 0

    def read_qa_dataset(self) -> List[Dict[str, Any]]:
        """Read all Q&A pairs from the input JSONL file"""
        qa_pairs = []
        
        if not os.path.exists(self.input_file):
            logger.error(f"❌ Input file {self.input_file} doesn't exist")
            raise FileNotFoundError(f"Input file {self.input_file} not found")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        qa_pair = json.loads(line.strip())
                        if self.validate_qa_pair(qa_pair):
                            qa_pairs.append(qa_pair)
                        else:
                            logger.warning(f"⚠️ Invalid Q&A pair on line {line_num}, skipping")
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Invalid JSON on line {line_num}: {e}")
                        continue
            
            logger.info(f"📄 Successfully loaded {len(qa_pairs)} Q&A pairs from {self.input_file}")
            return qa_pairs
            
        except Exception as e:
            logger.error(f"❌ Error reading {self.input_file}: {e}")
            raise

    def validate_qa_pair(self, qa_pair: Dict[str, Any]) -> bool:
        """Validate that a Q&A pair has the required structure"""
        required_fields = ["instruction", "input", "output"]
        return (isinstance(qa_pair, dict) and 
                all(field in qa_pair for field in required_fields) and
                all(isinstance(qa_pair[field], str) for field in required_fields) and
                all(len(qa_pair[field].strip()) > 0 for field in required_fields))

    def create_original_format(self, qa_pair: Dict[str, Any]) -> Dict[str, str]:
        """Create the original format variation"""
        return {
            "instruction": qa_pair["instruction"],
            "input": qa_pair["input"],
            "output": qa_pair["output"]
        }

    def create_rephrased_question(self, qa_pair: Dict[str, Any]) -> Dict[str, str]:
        """Create a variation with a rephrased question using LLM"""
        try:
            original_question = qa_pair["instruction"]
            context = qa_pair["input"]
            answer = qa_pair["output"]
            
            prompt = f"""Rephrase the following question to ask the same thing but with different wording. Keep the meaning identical but change the phrasing, word order, or style.

Original Question: {original_question}

Requirements:
1. Keep the same meaning and intent
2. Use different wording or sentence structure
3. Make it sound natural and conversational
4. Don't add new information or change the scope
5. Return ONLY the rephrased question, no additional text

Rephrased Question:"""

            # Apply rate limiting
            logger.debug(f"⏳ Applying rate limit delay: {self.rate_limit_delay} seconds")
            time.sleep(self.rate_limit_delay)
            
            # Get response from LLM
            response = self.llm_client.get_response(prompt)
            
            # Extract rephrased question
            rephrased_question = self.extract_rephrased_question(response)
            
            if rephrased_question and rephrased_question != original_question:
                return {
                    "instruction": rephrased_question,
                    "input": context,
                    "output": answer
                }
            else:
                # Fallback: create a simple variation
                return self.create_simple_rephrase(original_question, context, answer)
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to create rephrased question: {e}")
            return self.create_simple_rephrase(qa_pair["instruction"], qa_pair["input"], qa_pair["output"])

    def extract_rephrased_question(self, response) -> str:
        """Extract the rephrased question from LLM response"""
        try:
            # Handle different response formats
            if hasattr(response, 'content'):
                text = response.content.strip()
            elif hasattr(response, 'text'):
                text = response.text.strip()
            elif isinstance(response, str):
                text = response.strip()
            else:
                text = str(response).strip()
            
            # Clean up the response (remove any extra formatting)
            text = re.sub(r'^(Rephrased Question:|Question:|Answer:)\s*', '', text, flags=re.IGNORECASE)
            text = text.strip()
            
            # Ensure it ends with a question mark if it's a question
            if text and not text.endswith('?') and ('what' in text.lower() or 'how' in text.lower() or 
                                                   'when' in text.lower() or 'where' in text.lower() or 
                                                   'why' in text.lower() or 'who' in text.lower() or
                                                   'which' in text.lower() or 'is ' in text.lower() or
                                                   'are ' in text.lower() or 'do ' in text.lower() or
                                                   'does ' in text.lower() or 'can ' in text.lower()):
                text += '?'
            
            return text
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting rephrased question: {e}")
            return ""

    def create_simple_rephrase(self, question: str, context: str, answer: str) -> Dict[str, str]:
        """Create a simple rephrase without using LLM (fallback)"""
        # Simple rule-based rephrasing
        rephrased = question
        
        # Basic transformations
        if question.startswith("What is "):
            rephrased = question.replace("What is ", "Can you tell me what ", 1)
        elif question.startswith("How "):
            rephrased = question.replace("How ", "In what way ", 1)
        elif question.startswith("When "):
            rephrased = question.replace("When ", "At what time ", 1)
        elif question.startswith("Where "):
            rephrased = question.replace("Where ", "In which location ", 1)
        elif question.startswith("Why "):
            rephrased = question.replace("Why ", "For what reason ", 1)
        elif question.startswith("Who "):
            rephrased = question.replace("Who ", "Which person ", 1)
        
        return {
            "instruction": rephrased,
            "input": context,
            "output": answer
        }

    def create_context_focused_format(self, qa_pair: Dict[str, Any]) -> Dict[str, str]:
        """Create a variation that focuses more on the context"""
        original_question = qa_pair["instruction"]
        context = qa_pair["input"]
        answer = qa_pair["output"]
        
        # Create a context-focused question
        context_question = f"Based on the following information: '{context[:100]}...', {original_question.lower()}"
        
        return {
            "instruction": context_question,
            "input": context,
            "output": answer
        }

    def create_direct_answer_format(self, qa_pair: Dict[str, Any]) -> Dict[str, str]:
        """Create a variation with a more direct, concise format"""
        question = qa_pair["instruction"]
        context = qa_pair["input"]
        answer = qa_pair["output"]
        
        # Make the answer more direct
        direct_answer = answer
        if len(answer) > 100:
            # Try to extract the key information
            sentences = answer.split('. ')
            if len(sentences) > 1:
                direct_answer = sentences[0] + '.'
        
        return {
            "instruction": question,
            "input": context,
            "output": direct_answer
        }

    def expand_qa_pair(self, qa_pair: Dict[str, Any], index: int) -> List[Dict[str, str]]:
        """Expand a single Q&A pair into multiple variations"""
        variations = []
        
        logger.info(f"🔄 Expanding Q&A pair {index}")
        logger.debug(f"📝 Original question: {qa_pair['instruction'][:100]}...")
        
        try:
            # Variation 1: Original format
            variations.append(self.create_original_format(qa_pair))
            logger.debug("✅ Created original format variation")
            
            # Variation 2: Rephrased question (using LLM)
            rephrased_var = self.create_rephrased_question(qa_pair)
            variations.append(rephrased_var)
            logger.debug("✅ Created rephrased question variation")
            
            # Variation 3: Context-focused format
            context_var = self.create_context_focused_format(qa_pair)
            variations.append(context_var)
            logger.debug("✅ Created context-focused variation")
            
            # Optional Variation 4: Direct answer format (only if answer is long)
            if len(qa_pair["output"]) > 150:
                direct_var = self.create_direct_answer_format(qa_pair)
                variations.append(direct_var)
                logger.debug("✅ Created direct answer variation")
            
            logger.info(f"✅ Created {len(variations)} variations for Q&A pair {index}")
            return variations
            
        except Exception as e:
            logger.error(f"❌ Error expanding Q&A pair {index}: {e}")
            # Return at least the original
            return [self.create_original_format(qa_pair)]

    def save_variations(self, variations: List[Dict[str, str]]) -> bool:
        """Save variations to the output JSONL file"""
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                for variation in variations:
                    json_line = json.dumps(variation, ensure_ascii=False)
                    f.write(json_line + "\n")
            
            logger.debug(f"💾 Saved {len(variations)} variations to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save variations: {e}")
            return False

    def expand_dataset(self):
        """Main method to expand the entire dataset"""
        logger.info("🚀 Starting QA dataset expansion process")
        logger.info(f"📂 Input file: {self.input_file}")
        logger.info(f"💾 Output file: {self.output_file}")
        logger.info(f"⏱️ Rate limit delay: {self.rate_limit_delay} seconds")
        
        start_time = datetime.now()
        
        # Clear output file
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            logger.info(f"🗑️ Cleared existing output file: {self.output_file}")
        
        try:
            # Read the input dataset
            qa_pairs = self.read_qa_dataset()
            total_pairs = len(qa_pairs)
            
            if total_pairs == 0:
                logger.error("❌ No Q&A pairs to process. Exiting.")
                return
            
            logger.info(f"📋 Processing {total_pairs} Q&A pairs...")
            
            # Process each Q&A pair
            for idx, qa_pair in enumerate(qa_pairs, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"📄 Processing Q&A pair {idx}/{total_pairs}")
                logger.info(f"{'='*60}")
                
                # Expand the Q&A pair
                variations = self.expand_qa_pair(qa_pair, idx)
                
                if variations:
                    # Save variations
                    if self.save_variations(variations):
                        self.total_variations += len(variations)
                        self.processed_count += 1
                        logger.info(f"✅ Q&A pair {idx} expanded successfully ({len(variations)} variations)")
                    else:
                        self.failed_expansions += 1
                        logger.error(f"❌ Failed to save variations for Q&A pair {idx}")
                else:
                    self.failed_expansions += 1
                    logger.error(f"❌ No variations created for Q&A pair {idx}")
                
                # Progress update
                progress = (idx / total_pairs) * 100
                logger.info(f"📊 Progress: {progress:.1f}% ({idx}/{total_pairs})")
                logger.info(f"📈 Total variations generated so far: {self.total_variations}")
                
                # Estimated time remaining
                if idx > 0:
                    elapsed = datetime.now() - start_time
                    avg_time_per_pair = elapsed.total_seconds() / idx
                    remaining_pairs = total_pairs - idx
                    eta_seconds = remaining_pairs * avg_time_per_pair
                    eta_minutes = eta_seconds / 60
                    logger.info(f"⏰ Estimated time remaining: {eta_minutes:.1f} minutes")
        
        except KeyboardInterrupt:
            logger.warning("⚠️ Process interrupted by user")
        except Exception as e:
            logger.error(f"❌ Fatal error in dataset expansion: {e}")
        finally:
            # Final statistics
            end_time = datetime.now()
            total_time = end_time - start_time
            
            logger.info(f"\n{'='*60}")
            logger.info("📊 EXPANSION FINAL STATISTICS")
            logger.info(f"{'='*60}")
            logger.info(f"⏰ Total processing time: {total_time}")
            logger.info(f"📄 Q&A pairs processed: {self.processed_count}")
            logger.info(f"❌ Failed expansions: {self.failed_expansions}")
            logger.info(f"📝 Total variations generated: {self.total_variations}")
            logger.info(f"💾 Output saved to: {self.output_file}")
            
            if self.processed_count > 0:
                avg_variations_per_pair = self.total_variations / self.processed_count
                logger.info(f"📊 Average variations per Q&A pair: {avg_variations_per_pair:.1f}")
                
                # Calculate expansion ratio
                expansion_ratio = self.total_variations / self.processed_count if self.processed_count > 0 else 0
                logger.info(f"📈 Dataset expansion ratio: {expansion_ratio:.1f}x")
            
            logger.info("🏁 Dataset expansion completed!")


def main():
    """Main function to run the dataset expansion"""
    try:
        expander = QADatasetExpander()
        expander.expand_dataset()
    except Exception as e:
        logger.error(f"❌ Failed to initialize dataset expander: {e}")
        raise


if __name__ == "__main__":
    main()
