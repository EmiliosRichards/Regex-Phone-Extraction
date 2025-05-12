"""
Phone number extraction module for the Phone Extraction project.
"""
import re
import phonenumbers
import logging # Add logging import
from typing import List, Dict, Optional, Set, Any
from src.text.utils import clean_text # Assuming clean_text is still relevant upstream
from src.phone.validator import validate_phone_number_twilio # Import the Twilio validator

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(funcName)s:%(message)s')
log = logging.getLogger(__name__)

# --- Constants for Custom Validation ---
# TODO: Potentially load these from config or make them more dynamic
INVALID_PLACEHOLDERS: Set[str] = {"0000000000", "1111111111", "1234567890"} # Add more if needed
MIN_REPEATING_DIGITS: int = 5  # e.g., 55555
MIN_SEQUENTIAL_DIGITS: int = 8 # e.g., 12345678 or 87654321 - Increased sensitivity further

# Priority regions as specified
PRIORITY_REGIONS: Set[str] = {'DE', 'AT', 'CH'}

def _is_sequential(digits: str) -> bool:
    """Check for sequential digits (ascending or descending)."""
    if len(digits) < MIN_SEQUENTIAL_DIGITS:
        return False
    for i in range(len(digits) - MIN_SEQUENTIAL_DIGITS + 1):
        substring = digits[i:i + MIN_SEQUENTIAL_DIGITS]
        # Ensure it's actually numeric sequence, not just repeating (e.g., '11111')
        if len(set(substring)) <= 1:
            continue
        # Check ascending
        is_ascending = all(int(substring[j]) == int(substring[0]) + j for j in range(MIN_SEQUENTIAL_DIGITS))
        if is_ascending:
            return True
        # Check descending
        is_descending = all(int(substring[j]) == int(substring[0]) - j for j in range(MIN_SEQUENTIAL_DIGITS))
        if is_descending:
            return True
    return False

def is_valid_phone_number(
    number_str: str,
    region: Optional[str] = None,
    parsed_number: Optional[phonenumbers.PhoneNumber] = None
) -> bool:
    """
    Validate a phone number string using phonenumbers and custom logic.
    Does NOT filter based on region, only uses it for parsing hints.

    Args:
        number_str: The raw phone number string.
        region: The region code (e.g., 'DE') to assume if the number is not in E.164.
        parsed_number: Pre-parsed phonenumbers.PhoneNumber object (optional).

    Returns:
        Boolean indicating if the number is considered valid after checks.
    """
    log.debug(f"Validating number: '{number_str}', region: {region}")
    try:
        # Use pre-parsed number if available, otherwise parse it
        if parsed_number is None:
            log.debug("Parsing number string...")
            # The library handles '+' prefixed numbers correctly without a region hint.
            # Provide region hint for ambiguous local numbers.
            parsed_number = phonenumbers.parse(number_str, region)
            log.debug(f"Parsed result: {parsed_number}")
        else:
            log.debug("Using pre-parsed number.")

        # 1. Basic phonenumbers validation (possibility and validity)
        is_possible = phonenumbers.is_possible_number(parsed_number)
        is_valid_lib = phonenumbers.is_valid_number(parsed_number)
        log.debug(f"phonenumbers validation: is_possible={is_possible}, is_valid={is_valid_lib}")
        if not is_possible or not is_valid_lib:
             log.debug("Failed phonenumbers basic validation.")
             return False

        # 2. Custom Validation Logic
        # Get digits for pattern checks (use E164 for consistency, though national might also work)
        # Using NATIONAL format might be better for placeholder checks if they appear without country code
        national_digits = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        national_digits = re.sub(r'\D', '', national_digits) # Remove formatting
        e164_digits = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        e164_digits_only = re.sub(r'\D', '', e164_digits)
        log.debug(f"Digits for custom checks: national='{national_digits}', e164='{e164_digits_only}'")

        # Check for invalid placeholders (applied to the national number part and E164)
        if national_digits in INVALID_PLACEHOLDERS:
            log.debug(f"Failed placeholder check (national): '{national_digits}' in {INVALID_PLACEHOLDERS}")
            return False
        if e164_digits_only in INVALID_PLACEHOLDERS:
             log.debug(f"Failed placeholder check (E164): '{e164_digits_only}' in {INVALID_PLACEHOLDERS}")
             return False
        log.debug("Passed placeholder check.")


        # Check for excessive repeating digits (e.g., 000000, 111111)
        repeating_match = re.search(r'(\d)\1{' + str(MIN_REPEATING_DIGITS - 1) + r',}', national_digits)
        log.debug(f"Repeating digit check (min {MIN_REPEATING_DIGITS}) on '{national_digits}': {'Found' if repeating_match else 'Not Found'}")
        if repeating_match:
            log.debug("Failed repeating digit check.")
            return False
        log.debug("Passed repeating digit check.")

        # Check for sequential digits (e.g., 123456, 987654)
        is_seq = _is_sequential(national_digits)
        log.debug(f"Sequential digit check (min {MIN_SEQUENTIAL_DIGITS}) on '{national_digits}': {is_seq}")
        if is_seq:
            log.debug("Failed sequential digit check.")
            return False
        log.debug("Passed sequential digit check.")

        # 3. Region check is NOT done here for filtering, only classification later.

        log.debug(f"Number '{number_str}' PASSED all validation checks.")
        return True # Passed all checks

    except phonenumbers.NumberParseException as e:
        # If parsing fails, it's not a valid number in the expected format
        log.debug(f"Parsing failed: {e}")
        return False
    except Exception as e:
        # Catch any other unexpected errors during validation
        log.error(f"Unexpected error during validation for '{number_str}': {e}", exc_info=True) # Log unexpected errors with traceback
        return False


def extract_phone_numbers(text: str, default_region: str = 'DE') -> List[Dict[str, Any]]:
    """
    Extract, validate, and classify phone numbers from text using the phonenumbers library.

    Args:
        text: Input text string.
        default_region: The default region (e.g., 'DE', 'US') to assume for numbers
                        that are not in international E.164 format. Helps parsing ambiguity.

    Returns:
        List of dictionaries, each containing:
            'original': The raw matched string from the text.
            'e164': The validated number in E.164 format (e.g., +49...).
            'region': The detected region code for the number (e.g., 'DE', 'US', 'Unknown').
            'priority_region': Boolean indicating if the region is in the PRIORITY_REGIONS set.
            'position': The starting position (index) of the match in the original text.
            'validation_api': Dictionary containing results from the external API validation (if performed).
                'api_status': Status of the API call ('successful', 'failed', 'not_attempted').
                'is_valid': Boolean result from API (if successful), else None.
                'type': Number type from API (e.g., 'mobile', 'landline'), else None.
                'error_message': API error message, if any.
                'details': Other details returned by the API.
    """
    # Optional: Clean the text if needed before processing
    # text = clean_text(text)

    found_numbers: List[Dict[str, Any]] = []
    seen_e164_numbers: Set[str] = set() # To avoid adding duplicates

    # Use PhoneNumberMatcher for robust extraction. It finds potential numbers.
    # We then validate each potential number rigorously.
    try:
        matcher = phonenumbers.PhoneNumberMatcher(text, default_region)
        for match in matcher:
            number_str = match.raw_string
            parsed_num = match.number # The library's parsed representation
            log.debug(f"Matcher found: raw='{number_str}', parsed={parsed_num}, region_hint='{default_region}'") # Log what matcher found

            # Perform validation using our enhanced function
            if is_valid_phone_number(number_str, region=default_region, parsed_number=parsed_num):
                try:
                    # Format to E.164 for standardization and deduplication key
                    e164_format = phonenumbers.format_number(
                        parsed_num, phonenumbers.PhoneNumberFormat.E164
                    )

                    # Deduplicate based on the standardized E.164 format
                    if e164_format not in seen_e164_numbers:
                        seen_e164_numbers.add(e164_format)

                        # Get region code and classify priority
                        region_code = phonenumbers.region_code_for_number(parsed_num)
                        is_priority = region_code in PRIORITY_REGIONS

                        # --- Call External Validation API ---
                        api_validation_result = validate_phone_number_twilio(e164_format)
                        # ------------------------------------

                        found_numbers.append({
                            'original': number_str,
                            'e164': e164_format,
                            'region': region_code if region_code else "Unknown",
                            'priority_region': is_priority,
                            'position': match.start,
                            'validation_api': { # Add API results
                                'api_status': api_validation_result.get('api_status'),
                                'is_valid': api_validation_result.get('is_valid'),
                                'type': api_validation_result.get('details', {}).get('type'),
                                'error_message': api_validation_result.get('error_message'),
                                'details': api_validation_result.get('details', {}) # Include all details
                            }
                        })
                except Exception as format_error:
                    # Handle potential errors during formatting or region detection
                    # TODO: Consider logging the error and the number_str
                    # print(f"Error formatting/classifying number {number_str}: {format_error}")
                    continue # Skip this number if formatting/region detection fails

    except Exception as matcher_error:
         # Catch potential errors during the matching process itself
         # TODO: Consider logging this error
         # print(f"Error during phone number matching: {matcher_error}")
         pass # Continue if matching fails for some reason


    # Sort results by their original position in the text
    found_numbers.sort(key=lambda x: x['position'])

    return found_numbers