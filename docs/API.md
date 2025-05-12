# Phone Extraction Project - API Documentation

This document provides detailed information about the API of the Phone Extraction project.

## Module Structure

### `src.text` Package

#### `src.text.normalizer` Module

##### `normalize_text(text: Union[str, bytes], encoding: Optional[str] = None) -> str`

Normalizes text to UTF-8 encoding. Attempts to detect encoding if not provided.

- **Parameters:**
  - `text`: Input text as string or bytes.
  - `encoding`: Optional encoding to try first (if None, will be detected using `chardet`).
- **Returns:** Normalized text as UTF-8 string.
- **Raises:** `TypeError` if input text is not str or bytes.

##### `clean_text(text: str) -> str`

Cleans text by removing unnecessary characters (e.g., excessive whitespace, non-printable characters) while preserving those useful for phone number detection.

- **Parameters:**
  - `text`: Input text string.
- **Returns:** Cleaned text string.

##### `normalize_and_clean(text: Union[str, bytes], encoding: Optional[str] = None) -> str`

Normalizes text to UTF-8 and cleans it in one step. This is a convenience function combining `normalize_text` and `clean_text`.

- **Parameters:**
  - `text`: Input text as string or bytes.
  - `encoding`: Optional encoding to try first.
- **Returns:** Normalized and cleaned text as UTF-8 string.

*(Note: The `process_scraped_texts`, `get_latest_scraping_dir`, and `normalize_latest_data` functions from the older `src.text.normalizer` or `src.text.utils` might be outdated or part of specific scripting rather than the core reusable API. The core functions are `normalize_text` and `clean_text`.)*

### `src.phone` Package

#### `src.phone.extractor` Module

##### `is_valid_phone_number(number_str: str, region: Optional[str] = None, parsed_number: Optional[phonenumbers.PhoneNumber] = None, api_validation_func: Optional[Callable] = None) -> bool`

Validates if a string or a pre-parsed `phonenumbers.PhoneNumber` object represents a legitimate phone number.
It uses the `phonenumbers` library for initial checks and then applies custom rules (placeholder, repeating digits, sequential digits).
Optionally, it can invoke an API validation function.

- **Parameters:**
  - `number_str`: The phone number string to validate.
  - `region`: The region code (e.g., "US", "DE") to use as a hint for parsing, especially for national numbers.
  - `parsed_number`: An optional pre-parsed `phonenumbers.PhoneNumber` object. If provided, `number_str` and `region` might be ignored for initial parsing.
  - `api_validation_func`: An optional callable function that takes an E.164 formatted number string and returns a validation dictionary (e.g., from Twilio).
- **Returns:** `True` if the number is considered valid after all checks, `False` otherwise.
- **Custom Validation Constants:**
    - `MIN_REPEATING_DIGITS = 5`
    - `MIN_SEQUENTIAL_DIGITS = 8`
    - `PLACEHOLDER_PATTERNS`: List of regex patterns for common placeholder numbers.

##### `extract_phone_numbers(text: str, default_region: Optional[str] = None, custom_patterns: Optional[List[Dict]] = None, use_twilio_validation: bool = False) -> List[Dict[str, Any]]`

Extracts, validates, and optionally formats phone numbers from a given text.
It uses `phonenumbers.PhoneNumberMatcher` for finding potential numbers and `is_valid_phone_number` for validation.
Twilio validation can be enabled.

- **Parameters:**
  - `text`: The input text string to search for phone numbers.
  - `default_region`: A region code (e.g., "US", "DE") to hint to the `PhoneNumberMatcher`, improving accuracy for national numbers.
  - `custom_patterns`: Optional list of custom regex patterns to use in addition to `PhoneNumberMatcher`. (Currently, primary reliance is on `PhoneNumberMatcher`).
  - `use_twilio_validation`: If `True` and Twilio credentials are set up, performs an additional validation step using the Twilio Lookup API via `src.phone.validator.validate_phone_number_twilio`.
- **Returns:** A list of dictionaries, where each dictionary represents a valid extracted phone number and contains:
    - `original`: The raw string as found in the text.
    - `e164`: The phone number in E.164 format (e.g., "+14155552671").
    - `region`: The region code inferred for the number (e.g., "US").
    - `priority_region`: Boolean, `True` if the number matched due to the `default_region` hint.
    - `position`: The starting index of the number in the original text.
    - `validation_api`: A dictionary containing results from the Twilio API if `use_twilio_validation` was `True` and the call was made. Includes keys like `api_status`, `is_valid`, `type`, `error_message`, `details`.

#### `src.phone.validator` Module

##### `init_twilio_client() -> Optional[twilio.rest.Client]`

Initializes and returns a Twilio REST client if `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` are found in environment variables (loaded from `.env`).

- **Returns:** A `twilio.rest.Client` instance or `None` if credentials are not configured.

##### `validate_phone_number_twilio(phone_number_e164: str) -> Dict[str, Any]`

Validates a phone number using the Twilio Lookup v2 API.
Requires Twilio client to be initialized (i.e., credentials in `.env`).

- **Parameters:**
  - `phone_number_e164`: The phone number string in E.164 format.
- **Returns:** A dictionary containing:
    - `api_status`: "successful", "failed", or "skipped".
    - `is_valid`: Boolean, `True` if Twilio considers the number valid.
    - `error_message`: Error message if the API call failed or the number is invalid.
    - `details`: A dictionary with additional information from Twilio (e.g., `type`, `carrier_name`, `country_code`).

#### `src.phone.formatter` Module

*(This module might be less central if formatting is handled directly by `phonenumbers` or is not a primary requirement. The functions below are based on its previous structure.)*

##### `format_phone_number(number: str, format_type: str = 'E164', region: Optional[str] = None) -> str`

Formats a phone number string into a specified format using the `phonenumbers` library.

- **Parameters:**
  - `number`: The phone number string to format.
  - `format_type`: The desired format. Common values from `phonenumbers.PhoneNumberFormat` include:
      - `E164` (e.g., "+14155552671")
      - `INTERNATIONAL` (e.g., "+1 415-555-2671")
      - `NATIONAL` (e.g., "(415) 555-2671" for US)
      - `RFC3966` (e.g., "tel:+1-415-555-2671")
  - `region`: The region code (e.g., "US", "DE") required for `NATIONAL` formatting.
- **Returns:** The formatted phone number string, or the original number if formatting fails.

### `src.analysis` Package

#### `src.analysis.statistics` Module

##### `generate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]`

Generates statistics from phone number extraction results.
Example statistics include total numbers found, unique numbers, counts by region, etc.

- **Parameters:**
  - `results`: A list of dictionaries, where each dictionary is an output from `extract_phone_numbers`.
- **Returns:** A dictionary containing various statistics.

##### `save_results(data_to_save: Any, output_dir: Path, filename_base: str, timestamp: Optional[str] = None) -> Dict[str, Path]`

Saves processed data (e.g., extracted numbers, statistics) to files in JSON and TXT formats.

- **Parameters:**
  - `data_to_save`: The data to be saved. If a list of dicts (extracted numbers), it saves both JSON and a simple TXT list. If a dict (statistics), it saves as JSON.
  - `output_dir`: The base directory to save the results.
  - `filename_base`: The base name for the output files (e.g., "phone_numbers", "statistics").
  - `timestamp`: An optional timestamp string to create a subdirectory within `output_dir`. If `None`, uses the current time.
- **Returns:** A dictionary mapping file types ("json", "txt") to their `Path` objects.

##### `print_statistics(stats: Dict[str, Any]) -> None`

Prints statistics to the console in a readable format.

- **Parameters:**
  - `stats`: Dictionary containing statistics, typically the output of `generate_statistics`.

## Command-line Scripts

Refer to `README.md` for updated information on running scripts and the main application. The scripts in the `scripts/` directory might need updates to align with the latest module APIs.

## Configuration

*   **Environment Variables (`.env` file):**
    *   `TWILIO_ACCOUNT_SID`: Your Twilio Account SID.
    *   `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token.
    These are used by `src.phone.validator` for API calls.
*   **`config/patterns.json`**: While present, the primary extraction mechanism has shifted to the `phonenumbers` library. This file might be used for highly specific custom patterns if needed but is not the main driver for general phone number identification.