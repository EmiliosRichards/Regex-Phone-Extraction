# Plan: SQL Query and Automated Excel Export for Phone Numbers

This document outlines the plan to implement an automated Excel export feature that collects phone numbers and related company information from the database at the end of the main extraction process.

## 1. Define the SQL Query

The SQL query will retrieve phone numbers, associated company names, company websites, sources where the phone number was found, and the phone number's status. It joins the `cleaned_phone_numbers` table with the `companies` table.

```sql
SELECT
    cpn.phone_number,
    c.company_name,
    c.website,
    cpn.sources,
    cpn.phone_status
FROM
    cleaned_phone_numbers cpn
JOIN
    companies c ON cpn.client_id = c.client_id;
```

## 2. Create New Python Script: `scripts/export_phone_numbers_to_excel.py`

This script will contain the logic for querying the database and generating the Excel file.

**Key components:**

*   **Function `generate_phone_numbers_excel_report()`:**
    *   **Imports:**
        *   `psycopg2` (for database interaction)
        *   `pandas` (for data manipulation and Excel export)
        *   `os` (for path manipulation, e.g., creating `data/reports/` directory)
        *   `datetime` (for timestamping the Excel file)
        *   `get_db_connection` from `src.db.utils`
        *   `get_logger` from `src.utils.logging_config`
    *   **Database Connection:** Establish a connection using `get_db_connection()`.
    *   **Query Execution:** Execute the SQL query defined above.
    *   **Data Fetching & Processing:**
        *   Fetch all results from the query.
        *   The `sources` column (an array in PostgreSQL) will be converted to a comma-separated string for better readability in Excel.
    *   **Pandas DataFrame Creation:**
        *   Load the fetched and processed data into a Pandas DataFrame.
        *   Column names: "Phone Number", "Company Name", "Website URL", "Sources", "Status".
    *   **Excel Export:**
        *   Define the output directory (e.g., `data/reports/`). Create this directory if it doesn't exist using `os.makedirs(exist_ok=True)`.
        *   Generate a timestamped filename (e.g., `phone_numbers_export_YYYYMMDD_HHMMSS.xlsx`).
        *   Use `pandas.DataFrame.to_excel()` to save the DataFrame. Set `index=False` to avoid writing the DataFrame index to Excel.
    *   **Error Handling:** Implement `try-except-finally` blocks for database operations and file writing to ensure robustness and proper resource cleanup (closing the database connection).
    *   **Logging:** Log key steps, successful export, and any errors encountered.
*   **Standalone Execution:** Include an `if __name__ == '__main__':` block to allow the script to be run independently for testing or manual report generation.

## 3. Integrate into Main Extraction Script

The Excel export functionality will be integrated into the existing main phone number extraction script (e.g., `main.py` or `scripts/extract_phones.py`).

*   **Import:** Import the `generate_phone_numbers_excel_report` function from `scripts.export_phone_numbers_to_excel`.
*   **Function Call:** At the end of the main extraction logic (after all phone numbers have been processed and saved to the database), add a call to `generate_phone_numbers_excel_report()`.
*   **Error Handling:** Wrap this call in a `try-except` block to catch and log any errors during report generation, ensuring that a failure in report generation does not halt the entire extraction process.

## 4. Update `requirements.txt`

The following Python packages need to be added to `requirements.txt` if they are not already present:

*   `pandas`
*   `openpyxl` (a dependency for Pandas to write `.xlsx` files)

## 5. Documentation (Optional but Recommended)

*   Add a brief section to the `README.md` or other project documentation explaining the new automated Excel report feature and how to locate the generated reports.

## Mermaid Diagram: Automated Process Flow

```mermaid
graph TD
    AA[Start Main Extraction Process] --> AB[Extract & Process Phone Numbers];
    AB --> AC[Update Database with Phone Numbers];
    AC -- Success --> AD{Call generate_phone_numbers_excel_report()};
    AD -- Success --> AE[Excel Report Generated];
    AD -- Failure --> AF[Log Report Generation Error];
    AE --> AG[End Main Extraction Process];
    AF --> AG;

    subgraph Excel Report Generation Module
        B{Connect to Database};
        C[Execute SQL Query];
        D[Fetch & Process Results];
        E[Create Pandas DataFrame];
        F[Export DataFrame to Excel];
        B --> C --> D --> E --> F;
    end
    AD --> B;