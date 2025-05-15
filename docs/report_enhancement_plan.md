# Phone Extraction Output Enhancement Plan

## 1. Objective

To improve the clarity and usefulness of the phone number extraction process output, with a primary focus on enhancing `report.txt` and streamlining the generated JSON files.

## 2. Analysis Summary

*   **"Unknown" Entries in `report.txt`**: Caused by the script `src/analysis/statistics.py` attempting to access phone number strings (`formatted` or `original`) at the top level of the number object, while the actual data resides within a nested `extraction_details` object (e.g., `extraction_details.e164`, `extraction_details.original`).
*   **Redundant JSON Files**: The current process generates:
    *   `data.json`: Comprehensive statistics and detailed phone number list.
    *   `phone_numbers.json`: Only the detailed phone number list (subset of `data.json`).
    *   `statistics.json`: Only the statistics summary (subset of `data.json`).
    It was determined that `phone_numbers.json` and `statistics.json` are redundant.
*   **Primary Data Source**: `data.json` should serve as the single source of truth for detailed JSON output.

## 3. Proposed Changes

### A. Modify `src/analysis/statistics.py` for `report.txt` Generation

*   **Correct Phone Number Display**:
    *   Update the logic in `save_results` (around line 172) to correctly access phone number representations. The preferred order of access for each number should be:
        1.  `number['extraction_details']['e164']`
        2.  `number['extraction_details']['original']`
        3.  `number['phone_number']` (top-level field)
    *   If none of these are available, display a message like "Number data missing" instead of "Unknown".

### B. Enhance `report.txt` Content and Structure

*   **Add Generation Timestamp**: Include a timestamp at the beginning of the report.
*   **Include Key Metrics**: Add a new "Extraction Metrics" section to display:
    *   **Country Code Counts**: From `stats_summary['country_codes']`.
    *   **Number Format Counts**: From `stats_summary['format_counts']`.
*   **Improve Phone Number Listing**: For each website, list numbers clearly, showing both the E.164 format and the original text if available.
    *   Example: `- +49525798580 (Original: +49 5257 9858 0)`
*   **Add Error Summary**: If `stats_summary['errors']` contains actual error messages, list them in a dedicated section.

### C. Streamline JSON Output in `src/analysis/statistics.py`

*   **Remove Redundant Files**:
    *   Modify the `save_results` function to stop creating `phone_numbers.json`.
    *   Modify the `save_results` function to stop creating `statistics.json`.
*   **Maintain `data.json`**: Ensure `data.json` continues to be generated with the full statistics summary and the complete list of extracted numbers and their details.

## 4. Proposed `report.txt` Structure

```
=== Phone Number Detection Report ===
Generated: YYYY-MM-DD HH:MM:SS

Overall Summary
-----------------
Total websites processed: X
Websites with phone numbers: Y
Total phone numbers found: Z

Extraction Metrics
------------------
Country Code Counts:
  +CC1: count_A
  +CC2: count_B
Number Format Counts:
  FormatName1: count_X
  FormatName2: count_Y

Detailed Results by Website
---------------------------
Website: [Website1 Name/URL]
  Extracted Numbers:
    - [Number1_E164_Format] (Original: [Number1_Original_Text])
    - [Number2_E164_Format] (Original: [Number2_Original_Text])
  (or "No phone numbers found")

Website: [Website2 Name/URL]
  Extracted Numbers:
    - ...

Processing Errors (if any)
--------------------------
  [Website_With_Error1]: [Error Message]
  (or "No errors reported")
```

### Mermaid Diagram of Proposed `report.txt` Structure:

```mermaid
graph TD
    Report("report.txt")
    Report --> Header("=== Phone Number Detection Report ===")
    Report --> Timestamp("Generated: [Timestamp]")
    
    Report --> GlobalStats("Overall Summary")
    GlobalStats --> TotalWebsites("Total websites processed: X")
    GlobalStats --> WebsitesWithNumbers("Websites with phone numbers: Y")
    GlobalStats --> TotalNumbersFound("Total phone numbers found: Z")

    Report --> Metrics("Extraction Metrics")
    Metrics --> CountryCodeCounts("Country Code Counts:")
    CountryCodeCounts --> CC1("  +CC1: count_A")
    CountryCodeCounts --> CC2("  +CC2: count_B")
    Metrics --> FormatCounts("Number Format Counts:")
    FormatCounts --> Format1("  FormatName1: count_X")
    FormatCounts --> Format2("  FormatName2: count_Y")
    
    Report --> PerWebsiteDetails("Detailed Results by Website")
    PerWebsiteDetails --> WebsiteEntry1("Website: [Website1 Name/URL]")
    WebsiteEntry1 --> ExtractedNumbers1("  Extracted Numbers:")
    ExtractedNumbers1 --> Num1_1("    - [Number1_E164_Format] (Original: [Number1_Original_Text])")
    ExtractedNumbers1 --> Num1_2("    - [Number2_E164_Format] (Original: [Number2_Original_Text])")
    WebsiteEntry1 --> NoNumbers1("  No phone numbers found (if applicable)")
    
    PerWebsiteDetails --> WebsiteEntry2("Website: [Website2 Name/URL]")
    WebsiteEntry2 --> ExtractedNumbers2("  Extracted Numbers:")
    ExtractedNumbers2 --> Num2_1("    - [Number_E164_Format] (Original: [Number_Original_Text])")

    Report --> ErrorSummary("Processing Errors (if any)")
    ErrorSummary --> ErrorEntry1("  [Website_With_Error1]: [Error Message]")
    ErrorSummary --> NoErrors("  No errors reported (if applicable)")