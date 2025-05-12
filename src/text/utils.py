"""
Text utility functions for the Phone Extraction project.
"""
import chardet
import unicodedata
import re
from typing import Union, Optional

def normalize_text(text: Union[str, bytes], encoding: Optional[str] = None) -> str:
    """
    Normalize text to UTF-8 encoding and clean it.
    
    Args:
        text: Input text as string or bytes
        encoding: Optional encoding to try first (if None, will be detected)
        
    Returns:
        Normalized text as UTF-8 string
    """
    if isinstance(text, str):
        # If already a string, normalize unicode characters
        normalized = unicodedata.normalize('NFKC', text)
        return normalized
    
    # If bytes, detect encoding if not specified
    if encoding is None:
        result = chardet.detect(text)
        encoding = result['encoding']
    
    try:
        # Try to decode with detected/specified encoding
        decoded = text.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        # Fallback to UTF-8 with replacement
        decoded = text.decode('utf-8', errors='replace')
    
    # Normalize unicode characters
    normalized = unicodedata.normalize('NFKC', decoded)
    return normalized

def clean_text(text: str) -> str:
    """
    Clean text by removing unnecessary characters while preserving those useful for phone number detection.
    
    Args:
        text: Input text string
        
    Returns:
        Cleaned text string
    """
    # Convert to string if not already
    text = str(text)
    
    # Store if the original text had script tags
    had_script_tags = bool(re.search(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', text, flags=re.IGNORECASE))
    
    # Remove HTML script tags and their content
    text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', ' ', text, flags=re.IGNORECASE)
    
    # Remove other HTML tags
    text = re.sub(r'<[^>]*>', ' ', text)
    
    # Replace common phone number separators with spaces
    separators = ['-', '.', '/', '\\', '|', '_']
    for sep in separators:
        text = text.replace(sep, ' ')
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Keep only characters that could be part of a phone number or its context
    # This includes: digits, spaces, parentheses, plus sign, basic punctuation, and alphabetic characters
    allowed_chars = r'[0-9a-zA-Z\s\(\)\+\.\,\;\:\!\?\-]'
    text = ''.join(char for char in text if re.match(allowed_chars, char) or unicodedata.category(char).startswith('L'))
    
    # Remove leading and trailing whitespace
    text = text.strip()
    
    # Add a trailing space if the original text had script tags
    if had_script_tags:
        text += " "
    
    # Remove any remaining control characters
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
    
    return text

def normalize_and_clean(text: Union[str, bytes], encoding: Optional[str] = None) -> str:
    """
    Normalize text to UTF-8 and clean it in one step.
    
    Args:
        text: Input text as string or bytes
        encoding: Optional encoding to try first (if None, will be detected)
        
    Returns:
        Normalized and cleaned text as UTF-8 string
    """
    normalized = normalize_text(text, encoding)
    return clean_text(normalized)