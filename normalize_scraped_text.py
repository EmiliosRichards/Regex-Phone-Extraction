import os
import json
from pathlib import Path
from text_utils import normalize_and_clean
from datetime import datetime

def process_scraped_texts(base_dir: str) -> dict:
    """
    Process all text.txt files in the scraped data directory and normalize them.
    
    Args:
        base_dir: Base directory containing the scraped data
        
    Returns:
        Dictionary containing processing statistics
    """
    stats = {
        "total_files": 0,
        "processed_files": 0,
        "failed_files": [],
        "start_time": datetime.now().isoformat()
    }
    
    # Walk through all website directories
    for website_dir in Path(base_dir).glob("**/pages/*"):
        if not website_dir.is_dir():
            continue
            
        text_file = website_dir / "text.txt"
        if not text_file.exists():
            continue
            
        stats["total_files"] += 1
        
        try:
            # Read the original text file
            with open(text_file, 'rb') as f:
                original_text = f.read()
            
            # Normalize and clean the text
            normalized_text = normalize_and_clean(original_text)
            
            # Create a backup of the original file
            backup_file = text_file.with_suffix('.txt.bak')
            if not backup_file.exists():
                os.rename(text_file, backup_file)
            
            # Write the normalized text
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(normalized_text)
            
            stats["processed_files"] += 1
            
        except Exception as e:
            stats["failed_files"].append({
                "file": str(text_file),
                "error": str(e)
            })
    
    stats["end_time"] = datetime.now().isoformat()
    return stats

def main():
    # Get the most recent scraping directory
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
    print(f"Processing files in: {latest_dir}")
    
    # Process the files
    stats = process_scraped_texts(str(latest_dir))
    
    # Save processing statistics
    stats_file = latest_dir / "text_normalization_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Total files found: {stats['total_files']}")
    print(f"Successfully processed: {stats['processed_files']}")
    print(f"Failed files: {len(stats['failed_files'])}")
    if stats['failed_files']:
        print("\nFailed files:")
        for failed in stats['failed_files']:
            print(f"- {failed['file']}: {failed['error']}")

if __name__ == "__main__":
    main() 