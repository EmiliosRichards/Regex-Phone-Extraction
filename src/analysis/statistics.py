"""
Statistics and analysis module for the Phone Extraction project.
"""
from collections import defaultdict
from typing import List, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

def generate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate statistics from phone number extraction results.
    
    Args:
        results: List of dictionaries containing extraction results for each website
        
    Returns:
        Dictionary containing statistics
    """
    stats = {
        'total_websites': len(results),
        'websites_with_numbers': 0,
        'total_numbers_found': 0,
        'format_counts': defaultdict(int),
        'country_codes': defaultdict(int),
        'errors': [],
        'results': results
    }
    
    # Process each website's results
    for website_result in results:
        if website_result.get('numbers', []):
            stats['websites_with_numbers'] += 1
            stats['total_numbers_found'] += len(website_result['numbers'])
            
            # Count formats and country codes
            for number in website_result['numbers']:
                stats['format_counts'][number['format']] += 1
                
                # Extract country code if present
                if number['cleaned'].startswith('+'):
                    # Country codes can be 1, 2, or 3 digits
                    # Common country codes: +1 (US/Canada), +44 (UK), +49 (Germany), etc.
                    if number['cleaned'].startswith('+1'):
                        country_code = '1'  # North America
                    elif len(number['cleaned']) > 3 and number['cleaned'][1:3].isdigit():
                        # For other country codes, extract the first 2 digits if they form a valid country code
                        country_code = number['cleaned'][1:3]
                    else:
                        # Fallback
                        country_code = number['cleaned'][1:2]
                        
                    stats['country_codes'][country_code] += 1
    
    # Convert defaultdicts to regular dicts for JSON serialization
    stats['format_counts'] = dict(stats['format_counts'])
    stats['country_codes'] = dict(stats['country_codes'])
    
    return stats

def save_results(stats: Dict[str, Any], timestamp: str = None, output_dir: str = None) -> Dict[str, str]:
    """
    Save extraction results to files.
    
    Args:
        stats: Dictionary containing statistics and results
        timestamp: Optional timestamp string (if None, current time will be used)
        output_dir: Optional output directory (if None, default directory will be used)
        
    Returns:
        Dictionary containing paths to the saved files
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Use custom output directory or default
    base_dir = output_dir or os.environ.get('RESULTS_DIR', "data/results")
    
    # Create results directory if it doesn't exist
    results_dir = Path(f"{base_dir}/{timestamp}")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Save detailed JSON results
    json_file = results_dir / "phone_numbers.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # Create a simple text file with website names and numbers
    text_file = results_dir / "phone_numbers.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        for result in stats['results']:
            if result.get('numbers', []):
                f.write(f"\n{result['website']}:\n")
                for number in result['numbers']:
                    f.write(f"  {number['formatted']}\n")
    
    # Save statistics summary
    stats_file = results_dir / "statistics.json"
    stats_summary = {k: v for k, v in stats.items() if k != 'results'}
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_summary, f, indent=2, ensure_ascii=False)
    
    return {
        'json': str(json_file),
        'text': str(text_file),
        'stats': str(stats_file)
    }

def print_statistics(stats: Dict[str, Any]) -> None:
    """
    Print statistics to the console.
    
    Args:
        stats: Dictionary containing statistics
    """
    print("\n=== Phone Number Detection Summary ===")
    print(f"\nTotal websites processed: {stats['total_websites']}")
    
    if stats['total_websites'] > 0:
        percentage = (stats['websites_with_numbers'] / stats['total_websites'] * 100)
        print(f"Websites with phone numbers: {stats['websites_with_numbers']} ({percentage:.1f}%)")
    else:
        print(f"Websites with phone numbers: {stats['websites_with_numbers']} (0.0%)")
        
    print(f"Total phone numbers found: {stats['total_numbers_found']}")
    
    print("\nNumber formats found:")
    for format_name, count in stats['format_counts'].items():
        print(f"  {format_name}: {count}")
    
    print("\nCountry codes found:")
    for country_code, count in sorted(stats['country_codes'].items()):
        print(f"  +{country_code}: {count}")
    
    if stats.get('errors', []):
        print("\nErrors encountered:")
        for error in stats['errors']:
            print(f"  {error['website']}: {error['error']}")