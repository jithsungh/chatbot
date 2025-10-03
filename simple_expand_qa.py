"""
Simple QA Dataset Expansion Script (No LLM Required)

This script creates multiple variations of each Q&A pair without using LLM:
1. Original format
2. Rule-based rephrased question
3. Context-focused format
4. Concise answer format (if applicable)
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_qa_expansion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleQAExpander:
    def __init__(self):
        """Initialize the simple QA expander"""
        self.input_file = "qa.jsonl"
        self.output_file = "expanded_qa.jsonl"
        self.processed_count = 0
        self.total_variations = 0

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

    def create_rule_based_rephrase(self, question: str) -> str:
        """Create a rephrased question using simple rules"""
        rephrased = question
        question_lower = question.lower()
        
        # Rule-based transformations
        transformations = [
            # What questions
            (r'^What is (.+)\?$', r'Can you tell me what \1 is?'),
            (r'^What (.+)\?$', r'I would like to know what \1.'),
            
            # Who questions  
            (r'^Who is (.+)\?$', r'Can you identify who \1 is?'),
            (r'^Who (.+)\?$', r'I need to know who \1.'),
            
            # How questions
            (r'^How (.+)\?$', r'In what way \1?'),
            (r'^How can (.+)\?$', r'What is the method to \1?'),
            
            # When questions
            (r'^When (.+)\?$', r'At what time \1?'),
            
            # Where questions
            (r'^Where (.+)\?$', r'In which location \1?'),
            
            # Why questions
            (r'^Why (.+)\?$', r'For what reason \1?'),
            
            # Which questions
            (r'^Which (.+)\?$', r'What specific \1?'),
        ]
        
        for pattern, replacement in transformations:
            match = re.match(pattern, question, re.IGNORECASE)
            if match:
                rephrased = re.sub(pattern, replacement, question, flags=re.IGNORECASE)
                break
        
        # If no transformation worked, try some general approaches
        if rephrased == question:
            if question.startswith("What"):
                rephrased = question.replace("What", "Tell me what", 1)
            elif question.startswith("Who"):
                rephrased = question.replace("Who", "Please identify who", 1)
            elif question.startswith("How"):
                rephrased = question.replace("How", "Explain how", 1)
            elif question.startswith("When"):
                rephrased = question.replace("When", "At what time", 1)
            elif question.startswith("Where"):
                rephrased = question.replace("Where", "In what location", 1)
            elif question.startswith("Why"):
                rephrased = question.replace("Why", "For what reason", 1)
        
        return rephrased

    def create_variations(self, qa_pair: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create multiple variations of a Q&A pair"""
        variations = []
        original_q = qa_pair["instruction"]
        context = qa_pair["input"]
        answer = qa_pair["output"]
        
        # Variation 1: Original format
        variations.append({
            "instruction": original_q,
            "input": context,
            "output": answer
        })
        
        # Variation 2: Rephrased question
        rephrased_q = self.create_rule_based_rephrase(original_q)
        if rephrased_q != original_q:
            variations.append({
                "instruction": rephrased_q,
                "input": context,
                "output": answer
            })
        
        # Variation 3: Context-focused format
        if len(context) > 20:  # Only if context is meaningful
            context_snippet = context[:80] + "..." if len(context) > 80 else context
            context_focused_q = f"Based on this information: '{context_snippet}', {original_q.lower()}"
            variations.append({
                "instruction": context_focused_q,
                "input": context,
                "output": answer
            })
        
        # Variation 4: Concise answer (if answer is long)
        if len(answer) > 100:
            sentences = answer.split('. ')
            if len(sentences) > 1:
                concise_answer = sentences[0] + '.'
                variations.append({
                    "instruction": original_q,
                    "input": context,
                    "output": concise_answer
                })
        
        # Variation 5: Formal question format
        if not original_q.startswith(("Could you", "Can you", "Please")):
            if original_q.startswith("What"):
                formal_q = original_q.replace("What", "Could you tell me what", 1)
            elif original_q.startswith("Who"):
                formal_q = original_q.replace("Who", "Could you tell me who", 1)
            elif original_q.startswith("How"):
                formal_q = original_q.replace("How", "Could you explain how", 1)
            else:
                formal_q = f"Could you please answer: {original_q}"
            
            variations.append({
                "instruction": formal_q,
                "input": context,
                "output": answer
            })
        
        return variations

    def save_variations(self, variations: List[Dict[str, str]]) -> bool:
        """Save variations to the output JSONL file"""
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                for variation in variations:
                    json_line = json.dumps(variation, ensure_ascii=False)
                    f.write(json_line + "\n")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save variations: {e}")
            return False

    def expand_dataset(self):
        """Main method to expand the dataset"""
        logger.info("🚀 Starting simple QA dataset expansion")
        logger.info(f"📂 Input file: {self.input_file}")
        logger.info(f"💾 Output file: {self.output_file}")
        
        start_time = datetime.now()
        
        # Clear output file
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            logger.info(f"🗑️ Cleared existing output file")
        
        try:
            qa_pairs = self.read_qa_dataset()
            total_pairs = len(qa_pairs)
            
            logger.info(f"📋 Processing {total_pairs} Q&A pairs...")
            
            for idx, qa_pair in enumerate(qa_pairs, 1):
                # Create variations
                variations = self.create_variations(qa_pair)
                
                # Save variations
                if self.save_variations(variations):
                    self.total_variations += len(variations)
                    self.processed_count += 1
                
                # Progress logging every 50 pairs
                if idx % 50 == 0 or idx == total_pairs:
                    progress = (idx / total_pairs) * 100
                    logger.info(f"📊 Progress: {progress:.1f}% ({idx}/{total_pairs}) - {self.total_variations} variations created")
            
        except Exception as e:
            logger.error(f"❌ Error in expansion process: {e}")
        finally:
            end_time = datetime.now()
            total_time = end_time - start_time
            
            logger.info(f"\n{'='*60}")
            logger.info("📊 EXPANSION FINAL STATISTICS")
            logger.info(f"{'='*60}")
            logger.info(f"⏰ Total processing time: {total_time}")
            logger.info(f"📄 Q&A pairs processed: {self.processed_count}")
            logger.info(f"📝 Total variations generated: {self.total_variations}")
            logger.info(f"💾 Output saved to: {self.output_file}")
            
            if self.processed_count > 0:
                avg_variations = self.total_variations / self.processed_count
                logger.info(f"📊 Average variations per Q&A pair: {avg_variations:.1f}")
                expansion_ratio = self.total_variations / self.processed_count
                logger.info(f"📈 Dataset expansion ratio: {expansion_ratio:.1f}x")
            
            logger.info("🏁 Simple expansion completed!")


def main():
    try:
        expander = SimpleQAExpander()
        expander.expand_dataset()
    except Exception as e:
        logger.error(f"❌ Failed to run expansion: {e}")


if __name__ == "__main__":
    main()
