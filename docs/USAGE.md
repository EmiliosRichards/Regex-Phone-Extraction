# Phone Extraction Project - Usage Guide

This document provides detailed instructions on how to use the Phone Extraction project.

## Prerequisites

- Python 3.7 or higher
- Required packages (install via `pip install -r requirements.txt`)

## Data Organization

The project expects data to be organized in the following structure:

```
data/
├── raw/
│   └── [timestamp]/
│       ├── session.log
│       ├── summary.json
│       └── pages/
│           └── [domain]/
│               ├── page.html
│               ├── text.json
│               ├── text.txt
│               └── ocr/
├── processed/
│   └── [timestamp]/
│       └── pages/
│           └── [domain]/
│               └── text.txt
└── results/
    └── [timestamp]/
        ├── phone_numbers.json
        ├── phone_numbers.txt
        └── statistics.json
```

Where:
- `[timestamp]` is a directory named with the scraping date/time (e.g., `20250509_214446`)
- `[domain]` is a directory named with the website domain (e.g., `example_com`)
- `text.txt` contains the raw text extracted from the website

## Step 1: Text Normalization

The first step is to normalize the scraped text files:

```bash
python scripts/normalize_text.py
```

This will:
1. Find the most recent scraping directory in `data/raw/`
2. Process all `text.txt` files
3. Normalize encoding and clean the text
4. Write normalized text to the corresponding location in `data/processed/[timestamp]/`
5. Save processing statistics to `data/processed/[timestamp]/text_normalization_stats.json`

### Options

- `--dir PATH`: Process a specific directory instead of the most recent one
- `--output PATH`: Specify a custom output directory for normalized files

## Step 2: Phone Number Extraction

The second step is to extract phone numbers from the normalized text:

```bash
python scripts/extract_phones.py
```

This will:
1. Find the most recent scraping directory in `data/raw/`
2. Look for the corresponding processed directory in `data/processed/[timestamp]/`
3. Extract phone numbers from the normalized text files
4. Format the extracted numbers
5. Save results to `data/results/[timestamp]/phone_numbers.json`
6. Save a simple text list to `data/results/[timestamp]/phone_numbers.txt`
7. Save statistics to `data/results/[timestamp]/statistics.json`

### Options

- `--dir PATH`: Process a specific directory instead of the most recent one
- `--output PATH`: Specify a custom output directory for results

## Step 3: Results Analysis

The third step is to analyze the extraction results:

```bash
python scripts/analyze_results.py
```

This will:
1. Find the most recent results file
2. Generate and print statistics
3. Analyze country code distribution
4. Analyze format distribution

### Options

- `--file PATH`: Analyze a specific results file instead of the most recent one
- `--output PATH`: Save analysis results to a specified directory

## Running the Full Pipeline

To run all steps in sequence:

```bash
python main.py
```

### Options

- `--dir PATH`: Specify a custom directory containing scraped data
- `--file PATH`: Specify a custom results file for analysis
- `--skip-normalize`: Skip the normalization step
- `--skip-extract`: Skip the extraction step
- `--skip-analyze`: Skip the analysis step

## Customizing Phone Number Patterns

The phone number patterns used for extraction are defined in `config/patterns.json`. You can modify this file to add or adjust patterns for different phone number formats.

## Troubleshooting

### Common Issues

1. **No data directory found**: Ensure that the `data/scraping` directory exists and contains scraping subdirectories.

2. **No scraping directories found**: Ensure that there are timestamp-named directories within the `data/scraping` directory.

3. **No text files found**: Ensure that the website directories contain `text.txt` files.

### Logs

Log files are saved in the `logs/` directory with timestamps. Check these logs for detailed information about any errors that occur during processing.