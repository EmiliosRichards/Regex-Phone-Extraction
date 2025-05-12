"""
Tests for the phone number extractor module.
"""
import sys
import os
import unittest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.phone.extractor import extract_phone_numbers, is_valid_phone_number
from src.phone.formatter import format_phone_number

class TestPhoneExtractor(unittest.TestCase):
    """Test cases for the phone number extractor."""
    
    def test_is_valid_phone_number(self):
        """Test the phone number validation function."""
        # Valid phone numbers
        self.assertTrue(is_valid_phone_number("+49123456789"))
        self.assertTrue(is_valid_phone_number("0049123456789"))
        self.assertTrue(is_valid_phone_number("01234567890"))
        
        # Invalid phone numbers
        self.assertFalse(is_valid_phone_number("123"))  # Too short
        self.assertFalse(is_valid_phone_number("1234567890123456"))  # Too long
        self.assertFalse(is_valid_phone_number("00000000000"))  # Too many zeros
        self.assertFalse(is_valid_phone_number("12345678901234567890"))  # Too long
        self.assertFalse(is_valid_phone_number("11111111111"))  # Repeating digits
    
    def test_extract_phone_numbers(self):
        """Test the phone number extraction function."""
        # Test with German format
        text = "Kontaktieren Sie uns unter +49 (0) 123 456789 oder per E-Mail."
        numbers = extract_phone_numbers(text)
        self.assertEqual(len(numbers), 1)
        self.assertEqual(numbers[0]['format'], 'german')
        self.assertEqual(numbers[0]['cleaned'], '+49(0)123456789')
        
        # Test with international format
        text = "Contact us at +1 (234) 567-8900 or via email."
        numbers = extract_phone_numbers(text)
        self.assertEqual(len(numbers), 1)
        self.assertEqual(numbers[0]['format'], 'international')
        self.assertEqual(numbers[0]['cleaned'], '+12345678900')
        
        # Test with local format
        text = "Rufen Sie uns an: 0123 4567890"
        numbers = extract_phone_numbers(text)
        self.assertEqual(len(numbers), 1)
        self.assertEqual(numbers[0]['format'], 'local')
        self.assertEqual(numbers[0]['cleaned'], '01234567890')
        
        # Test with multiple numbers
        text = """
        Kontakt:
        Tel: +49 (0) 123 456789
        Fax: +49 (0) 123 456780
        Mobil: 0170 1234567
        """
        numbers = extract_phone_numbers(text)
        self.assertEqual(len(numbers), 3)
        
        # Test with no numbers
        text = "This text contains no phone numbers."
        numbers = extract_phone_numbers(text)
        self.assertEqual(len(numbers), 0)
    
    def test_format_phone_number(self):
        """Test the phone number formatting function."""
        # Test German format
        self.assertEqual(format_phone_number("+49123456789", "german"), "+49 123 456789")
        
        # Test international format
        self.assertEqual(format_phone_number("+12345678901", "international"), "+1 234 567 8901")
        
        # Test local format
        self.assertEqual(format_phone_number("1234567890", "local"), "(123) 456-7890")
        
        # Test invalid number
        self.assertEqual(format_phone_number("123", "international"), "123")

if __name__ == '__main__':
    unittest.main()