# Crawl Product Tiki
## Overview
This project focuses on collecting large-scale product data from **Tiki.vn**, using a dataset of approximately **200,000** product IDs.
## Objectives  
- Use **Python** to crawl product data from **Tiki** based on a predefined list of product IDs.
- Store the data in **JSON format**, with each file containing around **1,000 products**.
- Extract the following product fields:
  - `id`
  - `name`
  - `url_key`
  - `price`
  - `description`
  - `images_url`
- Transform and normalize the `description` field by:
  - Removing HTML tags and unnecessary markup.
  - Cleaning redundant whitespace and special characters.
  - Standardizing text structure for consistency and readability. 
## Features
- High-performance crawling using `ThreadPoolExecutor` to execute concurrent HTTP requests.
- Optimized crawling time while respecting rate limits.
- Batch processing and JSON output splitting (~1,000 products per file).
- Robust error handling and retry mechanism.
- Description cleaning and normalization pipeline.
- Scalable design for large datasets (200k+ products).
## Project Structure
```
crawl_product_tiki/
├── config/                 # Configuration files 
├── docs/
├── etl/                   # Data processing & transformation
├── pipelines/
├── src/
├── tests/
├── .gitignore           # Git ignore rules for the project
├── README.md
├── requirements.txt     # Python dependencies
```
## Output Format
Each JSON file contains a list of product objects with the following structure:
```json
{
  "id": 123456,
  "name": "Product name",
  "url_key": "product-url-key",
  "price": 199000,
  "description": "Normalized description text",
  "images_url": [
    "https://image-url-1"
  ]
}
```
## Tech Stack
- **Language**: Python 3.9+
- **HTTP Client**: requests
- **HTML Parsing**: beautifulsoup4
- **Data Format**: JSON
- **Progress Tracking**: tqdm
- **Environment Management**: venv
- **Version Control**: Git 
## Getting Started
### 1. Clone the repository
```bash
git clone https://github.com/Tbach1203/crawl_product_tiki.git
cd crawl_product_tiki
```
### 2. Install dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Configure database
Update database connection settings in the ```config/``` directory.
### 4. Run pipeline
```bash
python -m src.main
```