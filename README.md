# Fund Data Verification

A Python script that validates fund data against external APIs.

## Description

This script reads fund data from an Excel file, validates it against FundsNet and MZiQ APIs, and generates a new Excel file with validation results.

## Requirements

- Python 3.10+
- Required packages:
  - pandas
  - requests
  - openpyxl

## Installation

### Method 1: Native Python

1. Clone this repository
2. Install dependencies:

```bash
pip install pandas requests openpyxl
```

### Method 2: Docker

1. Clone this repository
2. Make sure Docker and Docker Compose are installed
3. No need to install dependencies manually - Docker will handle that

## Usage

### Method 1: Native Python

1. Place your input Excel file at `application/documents/entrada.xlsx` with the following columns:

   - MZIQ
   - CNPJ
   - Status

2. Run the script:

```bash
python application/main.py
```

### Method 2: Docker

1. Place your input Excel file at `application/documents/entrada.xlsx` with the following columns:

   - MZIQ
   - CNPJ
   - Status

2. Build and run with Docker Compose:

```bash
docker-compose up --build
```

Or run with Docker directly:

```bash
docker build -t funds-verifier .
docker run -v $(pwd)/application/documents:/app/application/documents funds-verifier
```

### Output

Check the output file at `application/documents/planilha-validada.xlsx` with additional columns:

- validado
- dataUltimoArquivamento
- idRedis

## Flow

1. The script reads the input Excel file
2. For each fund:
   - Queries FundsNet API using CNPJ to get fund description and last delivery date
   - Queries MZiQ API using fund description to get fund ID
   - Compares normalized CNPJ with the fund ID
3. Generates an output Excel file with validation results

## Error Handling

- The script continues processing even if some API calls fail
- Each step has appropriate error handling to ensure the script completes
- If an API call fails, the corresponding row will have `validado = False`
