# Plan to Update Database Record Creation (Revised V2)

This document outlines the plan to modify the process of creating records in the `raw_phone_numbers` table, ensuring `client_id`, `log_id`, and `page_id` are primarily sourced from their respective database tables using the URL as a key.

**I. [`src/db/utils.py`](src/db/utils.py) Modifications:**

1.  **Ensure `get_client_id_by_url(conn, url: str) -> Optional[str]` is robust:**
    *   This function already exists (lines 186-215 in the version reviewed) and queries `scraping_logs` for `client_id` based on `url_scraped`. This will be the primary method for fetching `client_id`.
2.  **Create `get_log_id_by_url(conn, url: str) -> Optional[Any]:`**
    *   **Action:** Add this new function.
    *   **Purpose:** Queries the `scraping_logs` table for `log_id`.
    *   **Input:** Database connection, URL string.
    *   **Logic:** `SELECT log_id FROM scraping_logs WHERE url_scraped = %s;` (or equivalent column name for the URL if different).
    *   **Output:** `log_id` if found, otherwise `None`.
    *   **Logging:** Include comprehensive logging for success, failure (e.g., DB error), and no-record-found scenarios.
3.  **Create `get_page_id_by_url(conn, url: str) -> Optional[Any]:`**
    *   **Action:** Add this new function.
    *   **Purpose:** Queries the `scraped_pages` table for `page_id`.
    *   **Input:** Database connection, URL string.
    *   **Logic:** `SELECT page_id FROM scraped_pages WHERE url = %s;` (or equivalent column name for the URL if different).
    *   **Output:** `page_id` if found, otherwise `None`.
    *   **Logging:** Include comprehensive logging for success, failure, and no-record-found scenarios.

**II. [`scripts/extract_phones.py`](scripts/extract_phones.py) Modifications:**

1.  **Update `get_metadata(text_file_path: Path, db_conn) -> Dict[str, Any]:`** (function starts around line 29 in the version reviewed)
    *   **a. URL Determination (Crucial First Step):**
        *   The first priority is to reliably determine the `url` for the current `text_file_path`. Review existing logic (e.g., lines 98, 108-115) to ensure `metadata["url"]` is populated with the most accurate and relevant URL available (from `text.json`, `metadata.json`, or `url.txt`). This URL will serve as the key for all subsequent database lookups.
    *   **b. Database Lookups (Primary Source for IDs):**
        *   If `metadata["url"]` is successfully determined and `db_conn` is available and operational:
            *   **`client_id` from DB:** Call `client_id_from_db = get_client_id_by_url(db_conn, metadata["url"])`. If `client_id_from_db` is found, update `metadata["client_id"] = client_id_from_db`. Log this action, indicating `client_id` was sourced from the database.
            *   **`log_id` from DB:** Call `log_id_from_db = get_log_id_by_url(db_conn, metadata["url"])`. If `log_id_from_db` is found, update `metadata["log_id"] = log_id_from_db`. Log this action.
            *   **`page_id` from DB:** Call `page_id_from_db = get_page_id_by_url(db_conn, metadata["url"])`. If `page_id_from_db` is found, update `metadata["page_id"] = page_id_from_db`. Log this action.
    *   **c. JSON Fallbacks (Secondary Source if DB Lookup Fails or ID is Not Found):**
        *   If `metadata["client_id"]` is still `None` (i.e., not found via URL in DB, or DB connection issue, or `get_client_id_by_url` returned `None`), *then* attempt to load it from `run_summary.json` (lines 65-77) and subsequently from page-level `text.json`/`metadata.json` (lines 93-102). Page-level JSON should override run-level JSON if both provide a `client_id`.
        *   Similarly, if `metadata["log_id"]` is `None` after the DB attempt, fall back to JSON sources (run summary, then page metadata).
        *   If `metadata["page_id"]` is `None` after the DB attempt, fall back to the page-level JSON source.
    *   **d. Path-based Fallbacks for `client_id` (Tertiary Source):**
        *   If `metadata["client_id"]` remains `None` after DB and all JSON attempts, the existing path-based fallbacks (lines 142-172) will be used as a last resort.
    *   **e. Final URL Check:** Ensure `metadata["url"]` (which will be inserted into the `raw_phone_numbers.url` field) is correctly and consistently populated throughout the `get_metadata` function.

2.  **Verify `process_text_file(text_file_path: Path, db_conn)`:** (function starts around line 253)
    *   No direct changes are anticipated for this function itself. The `data_to_store` dictionary (lines 326-338) will automatically use the `client_id`, `page_id`, `log_id`, and `url` values that have been populated by the revised `get_metadata` logic.

**III. Database Schema Considerations (For Awareness, No Direct Action in this Plan):**

*   It's recommended to ensure that the `url_scraped` column in the `scraping_logs` table and the `url` column in the `scraped_pages` table are indexed. This will improve the performance of the new lookup queries.
*   Confirm that the data types of `log_id` and `page_id` returned by the new utility functions are compatible with the corresponding columns in the `raw_phone_numbers` table.

**IV. Testing Strategy:**

*   **Unit Tests (for `src/db/utils.py`):**
    *   Test `get_log_id_by_url` and `get_page_id_by_url` with mock database connections:
        *   Scenario: URL exists, ID is returned.
        *   Scenario: URL does not exist, `None` is returned.
        *   Scenario: Database error occurs.
    *   Test `get_client_id_by_url` (existing function) similarly if not already covered.
*   **Integration Tests (for `scripts/extract_phones.py`):**
    *   Test `get_metadata` with various mock `text_file_path` structures and mock `db_conn` objects:
        *   Scenario 1: All IDs (`client_id`, `log_id`, `page_id`) are successfully fetched from the (mocked) database.
        *   Scenario 2: DB fails to provide `client_id`; it falls back to JSON, then to path-based logic.
        *   Scenario 3: DB fails to provide `log_id`; it falls back to JSON.
        *   Scenario 4: DB fails to provide `page_id`; it falls back to JSON.
        *   Scenario 5: URL cannot be determined from input files; ensure graceful handling.
        *   Scenario 6: JSON files have values, but DB also has values; ensure DB values take precedence.
    *   Test the end-to-end `process_text_file` and `insert_raw_phone_number` flow with a test database instance:
        *   Verify that the `raw_phone_numbers` table is populated with the correctly sourced `client_id`, `log_id`, `page_id`, and `url`.

**Mermaid Diagram of Proposed Changes (Revised V2):**

```mermaid
graph TD
    A[extract_phones.py: main] --> B{Process Text File}
    B --> C[get_metadata]

    subgraph "get_metadata Logic"
        C_URL[1. Determine URL from files]
        C_URL --> C_DB_CHECK{URL Found & DB Connected?}
        
        C_DB_CHECK -- Yes --> C_DB_CLIENT[2a. DB: get_client_id_by_url]
        C_DB_CLIENT --> C_META_CLIENT_DB[Update metadata.client_id]
        
        C_DB_CHECK -- Yes --> C_DB_LOG[2b. DB: get_log_id_by_url]
        C_DB_LOG --> C_META_LOG_DB[Update metadata.log_id]

        C_DB_CHECK -- Yes --> C_DB_PAGE[2c. DB: get_page_id_by_url]
        C_DB_PAGE --> C_META_PAGE_DB[Update metadata.page_id]

        C_DB_CHECK -- No/DB Fail --> C_JSON_FALLBACK_CLIENT[3a. JSON Fallback for client_id]
        C_META_CLIENT_DB --> C_JSON_FALLBACK_CLIENT
        C_JSON_FALLBACK_CLIENT --> C_PATH_FALLBACK_CLIENT[4. Path Fallback for client_id]
        C_PATH_FALLBACK_CLIENT --> C_FINAL_META[Finalized Metadata]

        C_DB_CHECK -- No/DB Fail --> C_JSON_FALLBACK_LOG[3b. JSON Fallback for log_id]
        C_META_LOG_DB --> C_JSON_FALLBACK_LOG
        C_JSON_FALLBACK_LOG --> C_FINAL_META

        C_DB_CHECK -- No/DB Fail --> C_JSON_FALLBACK_PAGE[3c. JSON Fallback for page_id]
        C_META_PAGE_DB --> C_JSON_FALLBACK_PAGE
        C_JSON_FALLBACK_PAGE --> C_FINAL_META
    end
    
    C --> C_FINAL_META
    C_FINAL_META --> J[process_text_file uses Metadata]
    J --> K[Prepare data_to_store]
    K --> L[db_utils: insert_raw_phone_number]

    subgraph "src/db/utils.py (New/Existing)"
        C_DB_CLIENT
        C_DB_LOG
        C_DB_PAGE
        L
    end

    style C_DB_CLIENT fill:#lightgreen,stroke:#333,stroke-width:2px
    style C_DB_LOG fill:#lightgreen,stroke:#333,stroke-width:2px
    style C_DB_PAGE fill:#lightgreen,stroke:#333,stroke-width:2px