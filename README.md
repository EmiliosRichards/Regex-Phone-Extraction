# Phone Number Extraction Project

A Python project for extracting and analyzing phone numbers from scraped web content.

## Project Structure

```
phone-extraction/
├── src/                      # Source code
│   ├── text/                 # Text processing modules
│   │   ├── normalizer.py     # Text normalization
│   │   └── utils.py          # Text utilities
│   ├── phone/                # Phone number processing modules
│   │   ├── extractor.py      # Phone number extraction
│   │   └── formatter.py      # Phone number formatting
│   └── analysis/             # Analysis modules
│       └── statistics.py     # Statistics generation
├── scripts/                  # Command-line scripts
│   ├── normalize_text.py     # Text normalization script
│   ├── extract_phones.py     # Phone extraction script
│   └── analyze_results.py    # Results analysis script
├── data/                     # Data directories
│   ├── raw/                  # Raw scraped data
│   │   └── [timestamp]/      # Scraping session by timestamp
│   │       └── pages/        # Website pages
│   │           └── [domain]/ # Website domain
│   │               └── text.txt # Raw text content
│   ├── processed/            # Processed data
│   │   └── [timestamp]/      # Processing session by timestamp
│   │       └── pages/        # Website pages
│   │           └── [domain]/ # Website domain
│   │               └── text.txt # Normalized text content
│   └── results/              # Extraction results
│       └── [timestamp]/      # Results by timestamp
│           ├── phone_numbers.json # Detailed results
│           ├── phone_numbers.txt  # Simple text list
│           └── statistics.json    # Summary statistics
├── config/                   # Configuration files
│   ├── default.json          # Default configuration
│   └── patterns.json         # Phone number patterns
├── logs/                     # Log files
├── docs/                     # Documentation
└── main.py                   # Main entry point
```

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Full Pipeline

To run the entire pipeline (normalize text, extract phone numbers, analyze results):

```bash
python main.py
```

By default, this will process the most recent scraping directory.

### Command-line Options

- `--dir PATH`: Specify a custom directory containing scraped data
- `--file PATH`: Specify a custom results file for analysis
- `--skip-normalize`: Skip the normalization step
- `--skip-extract`: Skip the extraction step
- `--skip-analyze`: Skip the analysis step

### Running Individual Steps

#### Text Normalization

```bash
python scripts/normalize_text.py [--dir PATH]
```

#### Phone Number Extraction

```bash
python scripts/extract_phones.py [--dir PATH] [--output PATH]
```

#### Results Analysis

```bash
python scripts/analyze_results.py [--file PATH] [--output PATH]
```

## Data Flow

1. **Text Normalization**:
   - Reads raw scraped text files from `data/raw/[timestamp]/pages/[domain]/text.txt`
   - Normalizes encoding and cleans the text
   - Writes normalized text to `data/processed/[timestamp]/pages/[domain]/text.txt`
   - Original files remain unchanged

2. **Phone Extraction**:
   - Reads normalized text from `data/processed/[timestamp]/pages/[domain]/text.txt`
   - Extracts phone numbers using regex patterns
   - Writes results to `data/results/[timestamp]/`

3. **Analysis**:
   - Reads extraction results from `data/results/[timestamp]/`
   - Generates statistics and insights from the extracted phone numbers

## Configuration

The project uses JSON configuration files in the `config/` directory:

- `default.json`: General configuration settings
- `patterns.json`: Phone number regex patterns and formatting rules

## Results

Extraction results are saved in the `data/results/` directory with the following files:

- `phone_numbers.json`: Detailed extraction results in JSON format
- `phone_numbers.txt`: Simple text list of extracted phone numbers
- `statistics.json`: Summary statistics

## License

[MIT License](LICENSE)