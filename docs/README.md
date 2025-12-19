# 🛒 Project-2-Crawl-Product-Tiki
## 🔍 Overview
This project focuses on collecting large-scale product data from **Tiki.vn**, using a dataset of approximately **200,000** product IDs.
## 📌 Features
- Crawl data for **~200,000 Tiki product IDs** using Python  
- Save output as **JSON files chunked by ~1,000 products per file**  
- Extract and standardize key product fields:
  - `id`
  - `name`
  - `url_key`
  - `price`
  - `description`
  - `images_url`  
## 📂 Project Structure
```
Project-2-Crawl-Product-Tiki/
├── config/                 # Configuration files 
├── etl/                   # Data processing & transformation
├── input/                 # Input files
│   ├── products-0-200000.csv    # List of product IDs to crawl
├── product/              # output
├── .gitignore           # Git ignore rules for the project
├── requirements.txt     # Python dependencies
```

