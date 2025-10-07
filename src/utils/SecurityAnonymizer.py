"""
Security Anonymizer for Organization Names
Handles anonymization of organization names in prompts and responses for security purposes.
"""

import re
from typing import Dict, List, Tuple
from src.config import Config


class SecurityAnonymizer:
    def __init__(self):
        """Initialize the anonymizer with organization replacement mappings."""
        # Get organization names from config
        self.original_org = Config.ORGANIZATION
        self.dummy_org = Config.DUMMY_ORGANIZATION
        
        # Extract organization domains if available
        self.original_domain = getattr(Config, 'ORGANIZATION_DOMAIN', 'techmojo.in')
        
        # Build replacement mappings
        self.anonymization_map = self._build_anonymization_map()
        self.reverse_map = self._build_reverse_map()
        
        # Pre-compile regex patterns for better performance
        self._compile_patterns()

    def _build_anonymization_map(self) -> Dict[str, str]:
        """Build the anonymization mapping dictionary."""
        mapping = {}
        
        # Organization name variations
        if self.original_org and self.dummy_org:
            mapping[self.original_org] = self.dummy_org
            
            # Handle case variations
            mapping[self.original_org.lower()] = self.dummy_org.lower()
            mapping[self.original_org.upper()] = self.dummy_org.upper()
            
            # Handle short forms (e.g., "Techmojo" -> "Panexus")
            original_short = self._extract_main_name(self.original_org)
            dummy_short = self._extract_main_name(self.dummy_org)
            
            if original_short and dummy_short:
                mapping[original_short] = dummy_short
                mapping[original_short.lower()] = dummy_short.lower()
                mapping[original_short.upper()] = dummy_short.upper()
                mapping[original_short.title()] = dummy_short.title()
        
        # Domain variations
        if hasattr(Config, 'ORGANIZATION_DOMAIN'):
            # Convert techmojo.in -> panexus.in
            dummy_domain = self.original_domain.replace('techmojo', 'panexus')
            mapping[self.original_domain] = dummy_domain
            mapping[self.original_domain.upper()] = dummy_domain.upper()
        
        return mapping

    def _build_reverse_map(self) -> Dict[str, str]:
        """Build the reverse mapping dictionary for de-anonymization."""
        return {v: k for k, v in self.anonymization_map.items()}

    def _extract_main_name(self, full_name: str) -> str:
        """Extract the main organization name (e.g., 'Techmojo' from 'Techmojo Solutions Pvt Ltd')."""
        if not full_name:
            return ""
        
        # Split by common separators and take the first meaningful part
        words = re.split(r'[\s\-_]+', full_name)
        if words:
            return words[0]
        return full_name

    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance."""
        self.anonymization_patterns = []
        self.reverse_patterns = []
        
        # Sort by length (descending) to match longer strings first
        sorted_items = sorted(self.anonymization_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        for original, replacement in sorted_items:
            # Create word boundary pattern for whole word matches
            pattern = r'\b' + re.escape(original) + r'\b'
            self.anonymization_patterns.append((re.compile(pattern, re.IGNORECASE), replacement))
        
        # Build reverse patterns
        sorted_reverse = sorted(self.reverse_map.items(), key=lambda x: len(x[0]), reverse=True)
        for dummy, original in sorted_reverse:
            pattern = r'\b' + re.escape(dummy) + r'\b'
            self.reverse_patterns.append((re.compile(pattern, re.IGNORECASE), original))

    def anonymize_text(self, text: str) -> str:
        """
        Anonymize organization names in the given text.
        
        Args:
            text: Input text containing organization names
            
        Returns:
            str: Anonymized text with organization names replaced
        """
        if not text or not isinstance(text, str):
            return text
        
        anonymized_text = text
        
        # Apply all anonymization patterns
        for pattern, replacement in self.anonymization_patterns:
            anonymized_text = pattern.sub(replacement, anonymized_text)
        
        return anonymized_text

    def deanonymize_text(self, text: str) -> str:
        """
        Reverse the anonymization process to restore original organization names.
        
        Args:
            text: Anonymized text
            
        Returns:
            str: Text with original organization names restored
        """
        if not text or not isinstance(text, str):
            return text
        
        deanonymized_text = text
        
        # Apply all reverse patterns
        for pattern, original in self.reverse_patterns:
            deanonymized_text = pattern.sub(original, deanonymized_text)
        
        return deanonymized_text

    def anonymize_prompt(self, prompt: str) -> str:
        """
        Anonymize a prompt before sending to LLM.
        
        Args:
            prompt: The prompt to be sent to LLM
            
        Returns:
            str: Anonymized prompt
        """
        return self.anonymize_text(prompt)

    def deanonymize_response(self, response: str) -> str:
        """
        Deanonymize an LLM response to restore original organization names.
        
        Args:
            response: The response from LLM
            
        Returns:
            str: Response with original organization names restored
        """
        return self.deanonymize_text(response)

    def get_anonymization_stats(self) -> Dict[str, int]:
        """
        Get statistics about the anonymization mappings.
        
        Returns:
            dict: Statistics including number of mappings
        """
        return {
            "total_mappings": len(self.anonymization_map),
            "organization_variants": len([k for k in self.anonymization_map.keys() 
                                       if any(org_name.lower() in k.lower() 
                                             for org_name in [self.original_org, self.dummy_org] 
                                             if org_name)]),
            "domain_variants": len([k for k in self.anonymization_map.keys() if '.' in k])
        }

    def test_anonymization(self, test_texts: List[str] = None) -> List[Dict]:
        """
        Test the anonymization with sample texts.
        
        Args:
            test_texts: Optional list of test texts. If None, uses default test cases.
            
        Returns:
            list: Test results with original, anonymized, and deanonymized texts
        """
        if test_texts is None:
            test_texts = [
                f"What is {self.original_org}?",
                f"I work at {self.original_org} as a developer.",
                f"Contact us at info@{self.original_domain}",
                f"{self._extract_main_name(self.original_org)} is a great company.",
                f"TECHMOJO SOLUTIONS provides excellent services.",
            ]
        
        results = []
        for text in test_texts:
            anonymized = self.anonymize_text(text)
            deanonymized = self.deanonymize_text(anonymized)
            
            results.append({
                "original": text,
                "anonymized": anonymized,
                "deanonymized": deanonymized,
                "round_trip_success": text == deanonymized
            })
        
        return results


# Singleton instance for global use
_anonymizer_instance = None

def get_anonymizer() -> SecurityAnonymizer:
    """Get or create the singleton SecurityAnonymizer instance."""
    global _anonymizer_instance
    if _anonymizer_instance is None:
        _anonymizer_instance = SecurityAnonymizer()
    return _anonymizer_instance


# Example usage and testing
if __name__ == "__main__":
    # Test the anonymizer
    anonymizer = SecurityAnonymizer()
    
    print("🔒 Security Anonymizer Test")
    print("=" * 50)
    
    # Show mappings
    print("Anonymization Mappings:")
    for original, dummy in anonymizer.anonymization_map.items():
        print(f"  '{original}' -> '{dummy}'")
    
    print("\n" + "=" * 50)
    
    # Test anonymization
    test_results = anonymizer.test_anonymization()
    
    print("Test Results:")
    for i, result in enumerate(test_results, 1):
        print(f"\nTest {i}:")
        print(f"  Original:    {result['original']}")
        print(f"  Anonymized:  {result['anonymized']}")
        print(f"  Restored:    {result['deanonymized']}")
        print(f"  Round-trip:  {'✅' if result['round_trip_success'] else '❌'}")
    
    # Performance test
    print(f"\n{'=' * 50}")
    print("Performance Statistics:")
    stats = anonymizer.get_anonymization_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
