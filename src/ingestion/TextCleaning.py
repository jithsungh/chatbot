import re
from langchain.schema import Document as docu

def remove_head_and_foot(text, header_patterns=None, footer_patterns=None):
    # Note: You will need to customize these patterns for your specific documents
    if header_patterns is None:
        header_patterns = []  # Example: [r'Company Confidential']
    if footer_patterns is None:
        # Example pattern for "Page X of Y"
        footer_patterns = [r'Page \d+ of \d+']

    for pattern in header_patterns + footer_patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
    return text.strip()

def remove_special_char(text):
    special_chars = r'[^A-Za-z0-9\s\.,;:\'\"?\!\-\(\)\/\@]'
    text = re.sub(special_chars, '', text)    #remove special characters.
    return text.strip()

def reomve_repeted_string(text, pattern=r'\.{2,}'):
    text = re.sub(pattern, '.', text)
    return text.strip()

def remove_extra_space(text):
    text = re.sub(r'\n+', '\n', text)   # normalize newlines
    text = re.sub(r'[ \t]+', ' ', text) # normalize spaces
    return text.strip()

def preprocess_text(text):
    """Orchestrates all the cleaning steps for a single string of text."""
    text = remove_head_and_foot(text)
    text = remove_special_char(text)
    text = reomve_repeted_string(text)
    text = remove_extra_space(text)
    return text.strip()



def docu_after_cleaning(extracted_data: list[docu]) -> list[docu]:


    for item in extracted_data:
        # Get the raw text from the dictionary
        raw_text = item.page_content
        
        # Clean the text using your preprocessing function
        cleaned_text = preprocess_text(raw_text)
        
        # Update the 'page_content' with the cleaned text
        item.page_content = cleaned_text
        
    return extracted_data


