import os
from pathlib import Path
from text_utils import extract_phone_numbers, format_phone_number, normalize_and_clean
from collections import defaultdict
import json
from datetime import datetime

def test_phone_patterns():
    """Test phone number patterns with various examples."""
    test_cases = [
        # German format examples from real data
        "+49 (0) 74 24 - 9 40 40",  # From ZWT
        "+49 (0) 74 24 - 9 40 43 0",  # From ZWT
        
        # International formats
        "+1 (234) 567-8900",
        "+44 20 7123 4567",
        "+86 10 1234 5678",
        
        # Local formats
        "(234) 567-8900",
        "234-567-8900",
        "234.567.8900",
        
        # With extensions
        "+1 (234) 567-8900 ext. 123",
        "+49 123 4567890-123",
        
        # Edge cases
        "1234567890",  # No separators
        "123.456.7890 ext. 123",  # Extension with dot
        "+49-123-4567890",  # Dashes instead of spaces
        "0049 123 4567890",  # 00 prefix
        "Tel: +49 123 4567890",  # With label
        "Phone: (123) 456-7890",  # With label
        
        # Potential false positives
        "12345",  # Too short
        "1234567890123456",  # Too long
        "123-456-789",  # Invalid format
        "Product ID: 123-456-789",  # Not a phone number
        "Version 1.2.3.4",  # Version number
        "IP: 192.168.1.1",  # IP address
    ]
    
    print("Testing phone number detection patterns...\n")
    
    for test in test_cases:
        print(f"\nTesting: {test}")
        numbers = extract_phone_numbers(test)
        
        if numbers:
            for number in numbers:
                print(f"  Found {number['format']} number:")
                print(f"    Original: {number['original']}")
                print(f"    Cleaned: {number['cleaned']}")
                print(f"    Formatted: {format_phone_number(number['cleaned'], number['format'])}")
        else:
            print("  No phone number detected")

def test_real_data():
    """Test phone number detection on real scraped data."""
    data_dir = Path("data/scraping")
    if not data_dir.exists():
        print("No data directory found!")
        return
    
    # Find the most recent scraping directory
    scraping_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()], 
                         key=lambda x: x.name, 
                         reverse=True)
    
    if not scraping_dirs:
        print("No scraping directories found!")
        return
    
    latest_dir = scraping_dirs[0]
    print(f"\nTesting phone number detection on real data from: {latest_dir}\n")
    
    # Statistics tracking
    stats = {
        'total_websites': 0,
        'websites_with_numbers': 0,
        'total_numbers_found': 0,
        'format_counts': defaultdict(int),
        'country_codes': defaultdict(int),
        'errors': [],
        'results': []
    }
    
    # Process each website's text file
    for website_dir in latest_dir.glob("**/pages/*"):
        if not website_dir.is_dir():
            continue
        
        text_file = website_dir / "text.txt"
        if not text_file.exists():
            continue
        
        website_name = website_dir.name
        stats['total_websites'] += 1
        
        print(f"\nProcessing: {website_name}")
        
        try:
            # Read and normalize the text
            with open(text_file, 'rb') as f:
                text = f.read()
            normalized_text = normalize_and_clean(text)
            
            # Extract phone numbers
            numbers = extract_phone_numbers(normalized_text)
            
            website_result = {
                'website': website_name,
                'numbers': []
            }
            
            if numbers:
                stats['websites_with_numbers'] += 1
                stats['total_numbers_found'] += len(numbers)
                print(f"  Found {len(numbers)} phone number(s):")
                
                for number in numbers:
                    stats['format_counts'][number['format']] += 1
                    
                    # Extract country code if present
                    if number['cleaned'].startswith('+'):
                        country_code = number['cleaned'][1:3]
                        stats['country_codes'][country_code] += 1
                    
                    print(f"    {number['format']}: {number['original']}")
                    print(f"    Cleaned: {number['cleaned']}")
                    print(f"    Formatted: {format_phone_number(number['cleaned'], number['format'])}")
                    
                    website_result['numbers'].append({
                        'format': number['format'],
                        'original': number['original'],
                        'cleaned': number['cleaned'],
                        'formatted': format_phone_number(number['cleaned'], number['format'])
                    })
            else:
                print("  No phone numbers found")
            
            stats['results'].append(website_result)
                
        except Exception as e:
            error_msg = f"Error processing {text_file}: {str(e)}"
            print(f"  {error_msg}")
            stats['errors'].append({
                'website': website_name,
                'error': str(e)
            })
    
    # Generate summary
    print("\n=== Phone Number Detection Summary ===")
    print(f"\nTotal websites processed: {stats['total_websites']}")
    print(f"Websites with phone numbers: {stats['websites_with_numbers']} ({(stats['websites_with_numbers']/stats['total_websites']*100):.1f}%)")
    print(f"Total phone numbers found: {stats['total_numbers_found']}")
    
    print("\nNumber formats found:")
    for format_name, count in stats['format_counts'].items():
        print(f"  {format_name}: {count}")
    
    print("\nCountry codes found:")
    for country_code, count in sorted(stats['country_codes'].items()):
        print(f"  +{country_code}: {count}")
    
    if stats['errors']:
        print("\nErrors encountered:")
        for error in stats['errors']:
            print(f"  {error['website']}: {error['error']}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"phone_number_results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Create a simple text file with website names and numbers
    text_output_file = f"phone_numbers_{timestamp}.txt"
    with open(text_output_file, 'w', encoding='utf-8') as f:
        for result in stats['results']:
            if result['numbers']:
                f.write(f"\n{result['website']}:\n")
                for number in result['numbers']:
                    f.write(f"  {number['formatted']}\n")
    
    print(f"Simple phone number list saved to: {text_output_file}")

if __name__ == "__main__":
    print("=== Phone Number Detection Test Suite ===\n")
    
    # Test with predefined examples
    test_phone_patterns()
    
    # Test with real scraped data
    test_real_data() 