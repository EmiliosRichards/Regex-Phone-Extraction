# Phone Extraction Project - Usage Guide

This document provides detailed instructions on how to set up and use the Phone Extraction project.

## Prerequisites

- Python 3.7 or higher.
- Git (for cloning the repository).

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd phone-extraction
    ```

2.  **Create and activate a virtual environment:**
    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *(Replace `venv` with your preferred virtual environment name if desired.)*

3.  **Install required packages:**
    With your virtual environment activated, install dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables for Twilio API (Optional but Recommended):**
    For enhanced phone number validation using the Twilio Lookup API, you need to provide your Twilio credentials.
    *   Create a file named `.env` in the project root directory.
    *   Add your Account SID and Auth Token to this file:
        ```env
        TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        TWILIO_AUTH_TOKEN="your_auth_token_here"
        ```
    *   A `.env.example` file is provided as a template.
    *   **Important**: Ensure `.env` is added to your `.gitignore` file to prevent committing your credentials.

## Core Functionality

The primary functionalities of this project are encapsulated in the modules within the `src/` directory.

### Text Processing (`src.text.normalizer`)

-   **`normalize_text(text, encoding=None)`**: Converts text to a standard UTF-8 encoding.
-   **`clean_text(text)`**: Removes unwanted characters and whitespace.
-   **`normalize_and_clean(text, encoding=None)`**: A combination of the above two.

These functions prepare raw text for reliable phone number extraction.

### Phone Number Extraction and Validation (`src.phone.extractor`, `src.phone.validator`)

-   **`extract_phone_numbers(text, default_region=None, use_twilio_validation=False)`** (from `src.phone.extractor`):
    *   This is the main function for finding and validating phone numbers in a given text.
    *   It uses the `phonenumbers` library (specifically `PhoneNumberMatcher`) for robust identification of numbers in various international and national formats.
    *   The `default_region` (e.g., "US", "DE", "GB") is a crucial hint for correctly parsing numbers written in a national format (e.g., "089/123456" for Germany if `default_region="DE"`).
    *   It applies custom validation rules defined in `is_valid_phone_number` (e.g., checks for placeholders, repeating digits, sequential digits).
    *   If `use_twilio_validation=True` and Twilio credentials are set up in the `.env` file, it will call `validate_phone_number_twilio` for an additional layer of validation.
    *   Returns a list of dictionaries, each containing details about an extracted valid phone number (original string, E.164 format, region, position, API validation results if applicable).

-   **`is_valid_phone_number(number_str, region=None, parsed_number=None, api_validation_func=None)`** (from `src.phone.extractor`):
    *   Performs validation using `phonenumbers` library functions and custom logic (sequential digits, repeating digits, placeholders).
    *   The constants `MIN_REPEATING_DIGITS` (default 5) and `MIN_SEQUENTIAL_DIGITS` (default 8) control the sensitivity of these custom checks.

-   **`validate_phone_number_twilio(phone_number_e164)`** (from `src.phone.validator`):
    *   Contacts the Twilio Lookup v2 API to get validation information for a number (must be in E.164 format).
    *   Returns a dictionary with API status, validity, and other details from Twilio.

### Analysis (`src.analysis.statistics`)

-   **`generate_statistics(results)`**: Takes the list of extracted phone numbers and computes various statistics (e.g., total found, unique counts, counts by country).
-   **`save_results(data_to_save, output_dir, filename_base, timestamp=None)`**: Saves extracted data and statistics to JSON and TXT files.
-   **`print_statistics(stats)`**: Prints a summary of statistics to the console.

## Running the Application (Examples)

The `main.py` script provides a basic example of how to use these components together. You will likely adapt this or call the modules directly in your own application flow.

```python
# Example usage within a Python script:
from src.text.normalizer import normalize_and_clean
from src.phone.extractor import extract_phone_numbers
from src.analysis.statistics import generate_statistics, print_statistics, save_results
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv() # To load .env file for Twilio credentials

# 1. Sample Text
sample_text_filepath = "path/to/your/input_text_file.txt" # Or use a string directly
# Ensure this file exists or provide text directly
# For example:
# with open(sample_text_filepath, 'r', encoding='utf-8') as f:
#     raw_text = f.read()
raw_text = "Call us at +49 (176) 12345678 or 089/9876543. US: (212) 555-1212."


# 2. Normalize Text
normalized_text = normalize_and_clean(raw_text)
print(f"Normalized Text: {normalized_text[:200]}...") # Print a snippet

# 3. Extract Phone Numbers
# Provide a default_region if your text is likely to contain national numbers from a specific country
# Enable Twilio validation if .env is set up
extracted_numbers = extract_phone_numbers(
    normalized_text,
    default_region="DE", # Example: Germany
    use_twilio_validation=bool(os.getenv("TWILIO_ACCOUNT_SID"))
)
print(f"\nExtracted Numbers ({len(extracted_numbers)}):")
for num_data in extracted_numbers:
    print(f"  - Original: {num_data['original']}, E.164: {num_data['e164']}, Region: {num_data['region']}")
    if 'validation_api' in num_data and num_data['validation_api'].get('api_status') == 'successful':
        print(f"    Twilio Valid: {num_data['validation_api']['is_valid']}, Type: {num_data['validation_api'].get('type')}")

# 4. Generate Statistics (if numbers were extracted)
if extracted_numbers:
    stats = generate_statistics(extracted_numbers) # Pass the list of dicts directly
    print("\nStatistics:")
    print_statistics(stats)

    # 5. Save Results
    results_output_dir = Path("data/results")
    # Ensure the output directory exists
    # results_output_dir.mkdir(parents=True, exist_ok=True) # Create if it doesn't exist

    # saved_files = save_results(stats, results_output_dir, "extraction_summary")
    # print(f"\nSummary saved to: {saved_files.get('json')}")

    # To save the detailed list of numbers:
    # saved_numbers_files = save_results(extracted_numbers, results_output_dir, "phone_numbers_detailed")
    # print(f"Detailed numbers saved to: {saved_numbers_files.get('json')} and {saved_numbers_files.get('txt')}")
else:
    print("\nNo phone numbers extracted to generate statistics or save results.")

```

The scripts in the `scripts/` directory (`normalize_text.py`, `extract_phones.py`, `analyze_results.py`) provide command-line interfaces for some of these steps but may require updates to fully align with the latest module APIs and data handling.

## Testing

The project includes a suite of unit tests located in the `tests/` directory. To run the tests:

1.  Ensure your virtual environment is activated.
2.  Ensure all development dependencies (including `pytest`, `pytest-mock`) are installed via `pip install -r requirements.txt`.
3.  Navigate to the project root directory in your terminal.
4.  Run the `pytest` command:
    ```bash
    pytest
    ```
    Pytest will automatically discover and execute the tests.

## Customizing Phone Number Identification

-   **`phonenumbers` Library**: The primary mechanism for identifying and parsing phone numbers is the `phonenumbers` Python library. Its `PhoneNumberMatcher` is highly effective for various formats. The `default_region` parameter in `extract_phone_numbers` is key to its accuracy with national numbers.
-   **Custom Validation Rules**: The `is_valid_phone_number` function in `src.phone.extractor` contains custom logic to filter out common non-valid numbers (placeholders, excessive repeating/sequential digits). You can adjust the constants `MIN_REPEATING_DIGITS` and `MIN_SEQUENTIAL_DIGITS` in this module to fine-tune this behavior.
-   **`config/patterns.json`**: This file was intended for custom regex patterns. While the system currently relies more on `phonenumbers`, this file could be adapted if very specific, non-standard patterns need to be targeted, by modifying `extract_phone_numbers` to incorporate them.

## Troubleshooting

-   **Twilio Errors**: If `use_twilio_validation=True`, ensure your `.env` file is correctly set up with valid `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`. Check Twilio's API logs if issues persist.
-   **No Numbers Extracted**:
    *   Verify the `default_region` supplied to `extract_phone_numbers` is appropriate for your text data if it contains many national-format numbers.
    *   Check the `clean_text` function's behavior if you suspect important characters are being stripped.
    *   Review the custom validation logic in `is_valid_phone_number` if valid numbers seem to be filtered out.
-   **Test Failures**: Examine the `pytest` output for details on which assertions failed. The test files in `tests/` provide examples of expected behavior.

## Logs

The application uses Python's standard `logging` module. Configure logging as needed in your application entry point to control log level and output. Some modules (like `src.phone.validator`) log information about their operations.