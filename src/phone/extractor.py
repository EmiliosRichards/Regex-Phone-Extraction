"""
Phone number extraction module for the Phone Extraction project.
"""
import re
from typing import List, Dict
from src.text.utils import clean_text

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
    
    # Define regex patterns for different phone number formats in order of specificity
    # Use a list of tuples to maintain order (most specific first)
    patterns = [
        # German format (more specific) - updated to match the full number with country code
        ('german', r'\+49\s*(?:\(0\))?\s*(?:\d[\s-]?){8,12}\d'),
        
        # International format with country code - improved to better match various formats
        ('international', r'(?:\+|00)\d{1,3}\s*(?:\(\d{1,4}\))?\s*(?:[\d][\s\-\.]?){6,12}[\d]'),
        
        # Local format with area code
        ('local', r'\(?0\d{1,4}\)?[\s.-]?(?:\d[\s-]?){5,10}\d')
    ]
    
    found_numbers = []
    
    # Try each pattern in order
    for format_name, pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            number = match.group(0)
            
            # Clean the found number
            if format_name == 'german':
                # For German format, keep parentheses around the '0'
                cleaned_number = re.sub(r'[\s\-\.]', '', number)
            else:
                # For other formats, remove spaces, dashes, dots, and parentheses
                cleaned_number = re.sub(r'[\s\-\.\(\)]', '', number)
            
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
    
    # First, create a fully normalized version of each number for comparison
    normalized_numbers = []
    for number in found_numbers:
        # Create a copy of the number dict
        number_copy = number.copy()
        
        # Create a fully normalized version for comparison (remove all non-digits)
        comparison_key = re.sub(r'\D', '', number['cleaned'])
        
        # For German numbers with country code, remove the leading 0 after the country code
        if number['format'] == 'german' and '(0)' in number['cleaned']:
            comparison_key = re.sub(r'\+49\(0\)', '+49', comparison_key)
        
        number_copy['comparison_key'] = comparison_key
        normalized_numbers.append(number_copy)
    
    # Sort by format priority (german first, then international, then local)
    format_priority = {'german': 0, 'international': 1, 'local': 2}
    normalized_numbers.sort(key=lambda x: format_priority.get(x['format'], 99))
    
    # Now deduplicate based on the normalized comparison key
    for number in normalized_numbers:
        if number['comparison_key'] not in seen_numbers:
            seen_numbers.add(number['comparison_key'])
            # Remove the temporary comparison key before adding to results
            del number['comparison_key']
            unique_numbers.append(number)
    
    return unique_numbers