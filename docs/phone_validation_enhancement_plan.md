# Phone Number Validation Enhancement Plan

## 1. Problem Description

The current phone number extraction process incorrectly validates very short numeric strings (e.g., "16949") as valid phone numbers, particularly when a `default_region` like 'DE' (Germany) is used. This leads to inaccurate data in reports, as seen with "+4916949 (Original: 16949)" in `data/results/20250514_140527/report.txt`.

## 2. Analysis of Cause

*   The script `scripts/extract_phones.py` calls `extract_phone_numbers` from `src/phone/extractor.py` with `default_region='DE'`.
*   `src/phone/extractor.py` uses `phonenumbers.PhoneNumberMatcher` and then `is_valid_phone_number`.
*   Inside `is_valid_phone_number`, `phonenumbers.parse(number_str, region)` interprets ambiguous short numbers based on the `default_region`.
*   The `phonenumbers` library's `is_possible_number()` and `is_valid_number()` checks can pass for these short numbers if they resemble parts of a valid numbering plan (e.g., short codes or incomplete numbers).
*   The existing custom validation (placeholders, repeating/sequential digits) does not include a check for a minimum overall length of the National Significant Number (NSN).

## 3. Standard Phone Number Lengths (DE, AT, CH)

*   **Germany (DE):** National Significant Numbers (NSN) are typically 7 to 11 digits.
*   **Austria (AT):** NSNs are generally 7 to 10 digits.
*   **Switzerland (CH):** NSNs are consistently 9 digits long.

A 5-digit number like "16949" is significantly shorter than typical NSNs in these countries.

## 4. Proposed Solution: Minimum NSN Length Check

To filter out overly short numbers, a minimum length check for the National Significant Number (NSN) will be added to the validation logic.

*   **Minimum NSN Length (`MIN_NSN_LENGTH`):** **7 digits**. This value is chosen as a reasonable baseline for DE, AT, and CH.
*   **Code Modification Location:** The `is_valid_phone_number` function within `src/phone/extractor.py`.
*   **Logic:** After the standard `phonenumbers.is_valid_number()` check passes, the length of the `national_number` (obtained from the parsed `PhoneNumber` object) will be compared against `MIN_NSN_LENGTH`.

## 5. Code Change in `src/phone/extractor.py`

The following code will be inserted into the `is_valid_phone_number` function in `src/phone/extractor.py`, after the existing `phonenumbers.is_valid_number()` check (around line 93):

```python
        # (Existing code from src/phone/extractor.py)
        is_possible = phonenumbers.is_possible_number(parsed_number)
        is_valid_lib = phonenumbers.is_valid_number(parsed_number)
        log.debug(f"phonenumbers validation: is_possible={is_possible}, is_valid={is_valid_lib}")
        if not is_possible or not is_valid_lib:
             log.debug("Failed phonenumbers basic validation.")
             return False
        log.debug("Passed phonenumbers basic validation.") # Added for clarity

        # NEW: Check for minimum National Significant Number length
        MIN_NSN_LENGTH = 7 # This can be made configurable later if needed
        national_significant_number = str(parsed_number.national_number)
        if len(national_significant_number) < MIN_NSN_LENGTH:
            log.debug(f"Failed NSN length check: '{national_significant_number}' (len {len(national_significant_number)}) is shorter than min {MIN_NSN_LENGTH}")
            return False
        log.debug(f"Passed NSN length check (len {len(national_significant_number)} >= {MIN_NSN_LENGTH}).") # Added for clarity

        # (Rest of the custom validation logic: placeholders, repeating, sequential)
        # ...
```

## 6. Updated Validation Flow Diagram

```mermaid
graph TD
    A[Start Validation: is_valid_phone_number] --> B{Parse Number with phonenumbers};
    B -- Success --> C{Library Valid? (is_possible & is_valid)};
    B -- Fail --> Z[Return False: Invalid];
    C -- No --> Z;
    C -- Yes --> D{NSN Length >= MIN_NSN_LENGTH?};
    D -- No --> Z;
    D -- Yes --> E{Placeholder Check};
    E -- Fail --> Z;
    E -- Pass --> F{Repeating Digits Check};
    F -- Fail --> Z;
    F -- Pass --> G{Sequential Digits Check};
    G -- Fail --> Z;
    G -- Pass --> Y[Return True: Valid];