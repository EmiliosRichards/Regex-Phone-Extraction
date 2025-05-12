# Phone Extraction Project - API Documentation

This document provides detailed information about the API of the Phone Extraction project.

## Module Structure

### `src.text` Package

#### `src.text.utils` Module

##### `normalize_text(text: Union[str, bytes], encoding: Optional[str] = None) -> str`

Normalizes text to UTF-8 encoding.

- **Parameters:**
  - `text`: Input text as string or bytes
  - `encoding`: Optional encoding to try first (if None, will be detected)
- **Returns:** Normalized text as UTF-8 string

##### `clean_text(text: str) -> str`

Cleans text by removing unnecessary characters while preserving those useful for phone number detection.

- **Parameters:**
  - `text`: Input text string
- **Returns:** Cleaned text string

##### `normalize_and_clean(text: Union[str, bytes], encoding: Optional[str] = None) -> str`

Normalizes text to UTF-8 and cleans it in one step.

- **Parameters:**
  - `text`: Input text as string or bytes
  - `encoding`: Optional encoding to try first (if None, will be detected)
- **Returns:** Normalized and cleaned text as UTF-8 string

#### `src.text.normalizer` Module

##### `process_scraped_texts(base_dir: str) -> dict`

Processes all text.txt files in the scraped data directory and normalizes them.

- **Parameters:**
  - `base_dir`: Base directory containing the scraped data
- **Returns:** Dictionary containing processing statistics

##### `get_latest_scraping_dir() -> Path`

Gets the most recent scraping directory.

- **Returns:** Path to the most recent scraping directory

##### `normalize_latest_data() -> dict`

Normalizes the text data in the most recent scraping directory.

- **Returns:** Dictionary containing processing statistics

### `src.phone` Package

#### `src.phone.extractor` Module

##### `is_valid_phone_number(number: str) -> bool`

Validates if a string looks like a legitimate phone number.

- **Parameters:**
  - `number`: String to validate
- **Returns:** Boolean indicating if the string looks like a valid phone number

##### `extract_phone_numbers(text: str) -> List[Dict[str, str]]`

Extracts phone numbers from text using comprehensive regex patterns.

- **Parameters:**
  - `text`: Input text string
- **Returns:** List of dictionaries containing extracted phone numbers and their formats

#### `src.phone.formatter` Module

##### `format_phone_number(number: str, format: str = 'international') -> str`

Formats a phone number according to the specified format.

- **Parameters:**
  - `number`: Phone number string (digits only)
  - `format`: Desired output format ('international', 'local', or 'german')
- **Returns:** Formatted phone number string

##### `format_extracted_numbers(extracted_numbers: List[Dict[str, str]]) -> List[Dict[str, str]]`

Formats a list of extracted phone numbers.

- **Parameters:**
  - `extracted_numbers`: List of dictionaries containing extracted phone numbers
- **Returns:** List of dictionaries with formatted phone numbers added

### `src.analysis` Package

#### `src.analysis.statistics` Module

##### `generate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]`

Generates statistics from phone number extraction results.

- **Parameters:**
  - `results`: List of dictionaries containing extraction results for each website
- **Returns:** Dictionary containing statistics

##### `save_results(stats: Dict[str, Any], timestamp: str = None) -> Dict[str, str]`

Saves extraction results to files.

- **Parameters:**
  - `stats`: Dictionary containing statistics and results
  - `timestamp`: Optional timestamp string (if None, current time will be used)
- **Returns:** Dictionary containing paths to the saved files

##### `print_statistics(stats: Dict[str, Any]) -> None`

Prints statistics to the console.

- **Parameters:**
  - `stats`: Dictionary containing statistics

## Command-line Scripts

### `scripts.normalize_text`

Script to normalize text from scraped websites.

- **Usage:** `python scripts/normalize_text.py [--dir PATH] [--output PATH]`

### `scripts.extract_phones`

Script to extract phone numbers from normalized text files.

- **Usage:** `python scripts/extract_phones.py [--dir PATH] [--output PATH]`

### `scripts.analyze_results`

Script to analyze phone number extraction results.

- **Usage:** `python scripts/analyze_results.py [--file PATH] [--output PATH]`

### `scripts.init_project`

Script to initialize the project directory structure.

- **Usage:** `python scripts/init_project.py [--dir PATH]`

### `main`

Main entry point for the Phone Extraction project.

- **Usage:** `python main.py [--dir PATH] [--file PATH] [--skip-normalize] [--skip-extract] [--skip-analyze]`

## Configuration

### `config/default.json`

General configuration settings.

### `config/patterns.json`

Phone number regex patterns and formatting rules.