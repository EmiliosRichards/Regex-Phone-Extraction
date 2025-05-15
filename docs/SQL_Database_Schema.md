Here's your complete, clearly formatted SQL schema in markdown, perfect for direct use in your project documentation:

# 📚 SQL Database Schema

This document outlines the complete SQL schema structure designed for clear data management, logging, and phone number tracking within your scraping system.

---

## 📌 Table Overview

| Table                       | Description                                          |
| --------------------------- | ---------------------------------------------------- |
| **companies**               | Core details about each company                      |
| **raw\_phone\_numbers**     | Tracks every individual phone number extraction      |
| **cleaned\_phone\_numbers** | Aggregated, deduplicated phone numbers ready for use |
| **scraping\_logs**          | Logs of scraping tasks, results, and errors          |
| **scraped\_pages**          | Metadata about each scraped webpage                  |

---

## 🗂 SQL Table Definitions

### 1. Companies Table

*(Core company data. Already exists—provided for completeness.)*

```sql
CREATE TABLE companies (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT,
    website TEXT,
    company_phone TEXT,
    linkedin_url TEXT,
    facebook_url TEXT,
    twitter_url TEXT,
    industry TEXT,
    employees INTEGER,
    founded_year INTEGER,
    annual_revenue TEXT,
    number_of_retail_locations INTEGER,
    short_description TEXT,
    seo_description TEXT,
    keywords TEXT,
    technologies TEXT,
    street TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    address TEXT,
    apollo_account_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 2. Raw Phone Numbers Table

*(Detailed logging of each phone number extraction.)*

```sql
CREATE TABLE raw_phone_numbers (
    raw_phone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES companies(client_id),
    page_id UUID REFERENCES scraped_pages(page_id),
    log_id UUID REFERENCES scraping_logs(log_id),
    phone_number TEXT NOT NULL,
    url TEXT,
    source_page TEXT, -- e.g., homepage, about, linkedin, contact
    scrape_run_timestamp TIMESTAMP,
    notes TEXT,
    extracted_at TIMESTAMP DEFAULT NOW()
);
```

---

### 3. Cleaned Phone Numbers Table

*(Aggregated, deduplicated phone numbers.)*

```sql
CREATE TABLE cleaned_phone_numbers (
    cleaned_phone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES companies(client_id),
    phone_number TEXT NOT NULL,
    sources TEXT[], -- ['homepage', 'linkedin', etc.]
    occurrence_count INTEGER DEFAULT 1,
    phone_status TEXT, -- valid, invalid, pending_validation, needs_review
    confidence_score NUMERIC DEFAULT 0.0,
    last_validated TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(client_id, phone_number)
);
```

---

### 4. Scraping Logs Table

*(Tracks scraping operations, results, and errors.)*

```sql
CREATE TABLE scraping_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES companies(client_id),
    source TEXT, -- homepage, about, linkedin
    url_scraped TEXT,
    status TEXT, -- pending, completed, failed
    scraping_date TIMESTAMP DEFAULT NOW(),
    error_message TEXT
);
```

---

### 5. Scraped Pages Table

*(Stores metadata of each scraped webpage.)*

```sql
CREATE TABLE scraped_pages (
    page_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES companies(client_id),
    url TEXT NOT NULL,
    page_type TEXT, -- homepage, support, linkedin, about, contact, etc.
    scraped_at TIMESTAMP DEFAULT NOW(),
    raw_html_path TEXT, -- External file storage location
    plain_text_path TEXT, -- External file storage location
    summary TEXT,
    extraction_notes TEXT
);
```

---

## 🚀 Indexes for Enhanced Performance

To optimize query performance, implement these recommended indexes:

```sql
-- Companies Table Indexes
CREATE INDEX idx_companies_website ON companies(website);
CREATE INDEX idx_companies_company_name ON companies(company_name);

-- Raw Phone Numbers Table Indexes
CREATE INDEX idx_raw_phone_numbers_client_id ON raw_phone_numbers(client_id);
CREATE INDEX idx_raw_phone_numbers_phone_number ON raw_phone_numbers(phone_number);

-- Cleaned Phone Numbers Table Indexes
CREATE INDEX idx_cleaned_phone_numbers_client_id ON cleaned_phone_numbers(client_id);
CREATE INDEX idx_cleaned_phone_numbers_phone_number ON cleaned_phone_numbers(phone_number);

-- Scraping Logs Table Indexes
CREATE INDEX idx_scraping_logs_client_id ON scraping_logs(client_id);
CREATE INDEX idx_scraping_logs_url_scraped ON scraping_logs(url_scraped);

-- Scraped Pages Table Indexes
CREATE INDEX idx_scraped_pages_client_id ON scraped_pages(client_id);
CREATE INDEX idx_scraped_pages_url ON scraped_pages(url);
```

---

## ✅ Schema Overview & Usage Summary

Your structured database schema now clearly separates detailed extraction logs from aggregated, clean data for practical use:

* **Detailed occurrence logging:** `raw_phone_numbers`
* **Aggregated & verified phone numbers:** `cleaned_phone_numbers`
* **Scraping task tracking & error logging:** `scraping_logs`
* **Scraped webpage metadata:** `scraped_pages`
* **Company core data storage:** `companies`

---

✨ **This structured schema ensures robustness, clarity, and efficient querying, perfectly suited for your scraping and data-extraction pipeline.**
