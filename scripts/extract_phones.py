#!/usr/bin/env python3
"""
Script to extract phone numbers from normalized text files.
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.text.utils import normalize_and_clean
from src.phone.extractor import extract_phone_numbers
from src.phone.formatter import format_phone_number
from src.analysis.statistics import generate_statistics, save_results, print_statistics

def process_website_directory(website_dir):
    """Process a single website directory and extract phone numbers."""
    text_file = website_dir / "text.txt"
    if not text_file.exists():
        return None
    
    website_name = website_dir.name
    
    try:
        # Read and normalize the text
        with open(text_file, 'rb') as f:
            text = f.read()
        normalized_text = normalize_and_clean(text)
        
        # Extract phone numbers
        numbers = extract_phone_numbers(normalized_text)
        
        # Format the numbers
        formatted_numbers = []
        for number in numbers:
            formatted_numbers.append({
                'format': number['format'],
                'original': number['original'],
                'cleaned': number['cleaned'],
                'formatted': format_phone_number(number['cleaned'], number['format'])
            })
        
        return {
            'website': website_name,
            'numbers': formatted_numbers
        }
    
    except Exception as e:
        return {
            'website': website_name,
            'error': str(e),
            'numbers': []
        }

def process_scraping_directory(scraping_dir):
    """Process all websites in a processed scraping directory and extract phone numbers."""
    results = []
    errors = []
    
    # Get the timestamp from the directory name
    timestamp = scraping_dir.name
    
    # Look for the corresponding processed directory
    processed_dir = Path(f"data/processed/{timestamp}")
    if not processed_dir.exists():
        raise FileNotFoundError(f"Processed directory not found: {processed_dir}")
    
    # Process each website's text file from the processed directory
    for website_dir in processed_dir.glob("**/pages/*"):
        if not website_dir.is_dir():
            continue
        
        result = process_website_directory(website_dir)
        if result:
            if 'error' in result:
                errors.append({
                    'website': result['website'],
                    'error': result['error']
                })
            results.append(result)
    
    # Generate statistics
    stats = generate_statistics(results)
    stats['errors'] = errors
    
    return stats

def main():
    """Main function to extract phone numbers from normalized text files."""
    parser = argparse.ArgumentParser(description='Extract phone numbers from normalized text files.')
    parser.add_argument('--dir', type=str, help='Directory containing scraped data (default: latest)')
    parser.add_argument('--output', type=str, help='Output directory for results')
    
    args = parser.parse_args()
    
    try:
        # Determine the scraping directory to process
        if args.dir:
            scraping_dir = Path(args.dir)
        else:
            # Find the most recent scraping directory in data/raw
            data_dir = Path("data/raw")
            if not data_dir.exists():
                print("Error: No data/raw directory found!")
                return 1
                
            scraping_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()],
                                key=lambda x: x.name,
                                reverse=True)
            
            if not scraping_dirs:
                print("Error: No scraping directories found in data/raw!")
                return 1
                
            scraping_dir = scraping_dirs[0]
        
        print(f"Processing phone numbers from raw directory: {scraping_dir}")
        print(f"Using normalized text from processed directory: data/processed/{scraping_dir.name}")
        
        # Process the directory
        stats = process_scraping_directory(scraping_dir)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = save_results(stats, timestamp)
        
        # Print statistics
        print_statistics(stats)
        
        print(f"\nDetailed results saved to: {output_files['json']}")
        print(f"Simple phone number list saved to: {output_files['text']}")
        print(f"Statistics saved to: {output_files['stats']}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())