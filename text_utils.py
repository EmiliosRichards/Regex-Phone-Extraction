import chardet
import unicodedata
import re
from typing import Union, Optional, List, Dict

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
    
    # Replace common phone number separators with spaces
    separators = ['-', '.', '/', '\\', '|', '_']
    for sep in separators:
        text = text.replace(sep, ' ')
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Keep only characters that could be part of a phone number or its context
    # This includes: digits, spaces, parentheses, plus sign, and basic punctuation
    allowed_chars = r'[0-9\s\(\)\+\.\,\;\:\!\?]'
    text = ''.join(char for char in text if re.match(allowed_chars, char))
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
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

def is_valid_phone_number(number: str) -> bool:
    """
    Validate if a string looks like a legitimate phone number.
    
    Args:
        number: String to validate
        
    Returns:
        Boolean indicating if the string looks like a valid phone number
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', number)
    
    # Basic length validation (most phone numbers are between 8 and 15 digits)
    if len(digits) < 8 or len(digits) > 15:
        return False
        
    # Check for repeating patterns that might indicate non-phone numbers
    if re.search(r'(\d)\1{4,}', digits):  # 5 or more repeated digits
        return False
        
    # Check for sequential patterns that might indicate dates or other numbers
    if re.search(r'(19|20)\d{2}', digits):  # Looks like a year
        return False
        
    # Check for common non-phone number patterns
    if re.search(r'^0{3,}', digits):  # Starts with too many zeros
        return False
        
    return True

def extract_phone_numbers(text: str) -> List[Dict[str, str]]:
    """
    Extract phone numbers from text using comprehensive regex patterns.
    
    Args:
        text: Input text string
        
    Returns:
        List of dictionaries containing extracted phone numbers and their formats
    """
    # Clean the text first
    text = clean_text(text)
    
    # Define regex patterns for different phone number formats
    patterns = {
        # German format (more specific)
        'german': r'(?:(?:\+49|0049|49)|(?:\(0\)))\s*(?:\d[\s-]?){8,12}\d',
        
        # International format with country code
        'international': r'(?:\+|00)\d{1,3}[\s.-]?(?:\(0\))?\s*(?:\d[\s-]?){6,12}\d',
        
        # Local format with area code
        'local': r'\(?0\d{1,4}\)?[\s.-]?(?:\d[\s-]?){5,10}\d'
    }
    
    found_numbers = []
    
    # Try each pattern
    for format_name, pattern in patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            number = match.group(0)
            
            # Clean the found number
            cleaned_number = re.sub(r'[\s\-\.]', '', number)
            
            # Validate the number
            if is_valid_phone_number(cleaned_number):
                found_numbers.append({
                    'original': number,
                    'cleaned': cleaned_number,
                    'format': format_name,
                    'position': match.start()
                })
    
    # Remove duplicates (same number in different formats)
    unique_numbers = []
    seen_numbers = set()
    
    for number in sorted(found_numbers, key=lambda x: len(x['cleaned']), reverse=True):
        cleaned = re.sub(r'^0+', '', number['cleaned'])  # Remove leading zeros for comparison
        if cleaned not in seen_numbers:
            seen_numbers.add(cleaned)
            unique_numbers.append(number)
    
    return unique_numbers

def format_phone_number(number: str, format: str = 'international') -> str:
    """
    Format a phone number according to the specified format.
    
    Args:
        number: Phone number string (digits only)
        format: Desired output format ('international', 'local', or 'german')
        
    Returns:
        Formatted phone number string
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', number)
    
    # If not a valid phone number, return as is
    if not is_valid_phone_number(digits):
        return number
    
    if format == 'german':
        if digits.startswith('49'):
            digits = digits[2:]  # Remove country code
        if digits.startswith('0'):
            digits = digits[1:]  # Remove leading zero
        return f"+49 {digits[:3]} {digits[3:]}"
    
    elif format == 'international':
        if len(digits) >= 10:
            if digits.startswith('00'):
                digits = digits[2:]  # Remove 00 prefix
            if not digits.startswith('+'):
                digits = '+' + digits
            return f"{digits[:3]} {digits[3:6]} {digits[6:9]} {digits[9:]}"
    
    elif format == 'local':
        if len(digits) >= 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:10]}"
    
    return number  # Return original if no format matches 