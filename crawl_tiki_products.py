import pandas as pd
import requests
import json
# import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
}

# ==========================
# UTILITIES
# ==========================
def get_Id(df):
    return df['id'].tolist()

def clean_html(html_text):
    if html_text is None:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def product(data):
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "url_key": data.get("url_key"),
        "price": data.get("price"),
        "description": clean_html(data.get("description")),
        "images": data.get("images")[0].get("base_url") if data.get("images") else None
    }

# ==========================
# FILE MANAGEMENT
# ==========================
file_lock = threading.Lock()

PROCESSED_FILE = "processed_ids.txt"
ERROR_FILE = "error_ids.txt"
PRODUCT_DIR = "product"
os.makedirs(PRODUCT_DIR, exist_ok=True)

def load_processed_ids():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(int(line.strip()) for line in f if line.strip().isdigit())
    except:
        return set()

def save_processed_id(pid):
    with file_lock:
        with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{pid}\n")

def load_error_ids():
    if not os.path.exists(ERROR_FILE):
        return []
    with open(ERROR_FILE, "r", encoding="utf-8") as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]

def save_error_id(pid):
    with file_lock:
        errors = load_error_ids() 
        if pid in errors:         
            return
        with open(ERROR_FILE, "a", encoding="utf-8") as f:
            f.write(f"{pid}\n")

# ==========================
# FETCH PRODUCT
# ==========================
def fetch_product(product_id, retries=5):
    for _ in range(retries):
        response = requests.get("https://api.tiki.vn/product-detail/api/v1/products/{}".format(product_id), headers=headers, timeout=10)
        if response.status_code == 200:
            return product(response.json())
    return None

# ==========================
# SAVE BY CHUNK (1000 / file)
# ==========================
def save_chunk(chunk, chunk_index):
    filename = os.path.join(PRODUCT_DIR, f"products_{chunk_index}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(chunk, f, indent=4, ensure_ascii=False)
    print(f"Đã lưu file: {filename}")

# ==========================
# MAIN PROCESS
# ==========================
def info_products(ids, max_workers=15):
    processed_ids = load_processed_ids()
    print(f"Đã xử lý: {len(processed_ids)} sản phẩm")
    ids_to_run = [pid for pid in ids if pid not in processed_ids]
    print(f"Còn lại cần xử lý: {len(ids_to_run)} sản phẩm")

    chunk = []
    chunk_index = 1

    existing_files = [f for f in os.listdir(PRODUCT_DIR) if f.startswith("products_")]
    if existing_files:
        chunk_index = max(int(f.split("_")[1].split(".")[0]) for f in existing_files) + 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_product, pid): pid for pid in ids_to_run}
        for future in tqdm(as_completed(future_to_id), total=len(ids_to_run)):
            pid = future_to_id[future]
            try:
                result = future.result()
                if result:
                    chunk.append(result)
                    save_processed_id(pid)
                else:
                    save_error_id(pid)

                if len(chunk) >= 1000:
                    save_chunk(chunk, chunk_index)
                    chunk = []
                    chunk_index += 1
            except Exception as e:
                print(f"Error processing product {pid}: {e}")
                save_error_id(pid)
    if chunk:
        save_chunk(chunk, chunk_index)

# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    df = pd.read_csv("products-0-200000.csv")
    ids = get_Id(df)
    info_products(ids, max_workers=20)
