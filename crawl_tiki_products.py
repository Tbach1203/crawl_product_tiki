import pandas as pd
import requests
import json
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os

headers = {
    #Random user Agent để tránh block
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
}

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

file_lock = threading.Lock()

PROCESSED_FILE = "processed_ids.txt"
def load_processed_ids():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(int(line.strip()) for line in f if line.strip().isdigit())
    except:
        return set()

def save_processed_id(pid):
    with file_lock:  # tránh ghi đè khi nhiều thread chạy
        with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{pid}\n")

ERROR_FILE = "error_ids.txt"
def save_error_id(pid):
    with file_lock:
        with open(ERROR_FILE, "a", encoding="utf-8") as f:
            f.write(f"{pid}\n")

def fetch_product(product_id, retries=5):
    for _ in range(retries):
            response = requests.get(url = 'https://api.tiki.vn/product-detail/api/v1/products/{}'.format(product_id), headers=headers, timeout=8)
            if response.status_code == 200:
                return product(response.json())
    return None

def save_to_json_batch(batch, filename='products.json'):
    with file_lock:
        try:
            existing_data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    print("⚠ JSON lỗi, hệ thống tự sửa.")
                    existing_data = []
            existing_data.extend(batch)
            tmp_file = filename + ".tmp"
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
            os.replace(tmp_file, filename)
        except Exception as e:
            print(f"Error saving to JSON: {e}")

def info_products(ids, max_workers=15):
    processed_ids = load_processed_ids()
    print(f"Đã xử lý: {len(processed_ids)} sản phẩm")
    
    # CHỈ LẤY NHỮNG ID CHƯA XỬ LÝ
    ids_to_run = [pid for pid in ids if pid not in processed_ids]
    print(f"Còn lại cần xử lý: {len(ids_to_run)} sản phẩm")
    results = []
    batch_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {
            executor.submit(fetch_product, pid): pid
            for pid in ids_to_run
        }
        for future in tqdm(as_completed(future_to_id), total=len(ids_to_run)):
            product_id = future_to_id[future]
            try:
                result = future.result()
                if result:
                    batch_results.append(result)
                    results.append(result)
                    save_processed_id(product_id)  # ✔ CHỈ lưu nếu crawl thành công
                else:
                    save_error_id(product_id)
                # Ghi batch mỗi 50 sản phẩm
                if len(batch_results) >= 50:
                    save_to_json_batch(batch_results)
                    batch_results = []
            except Exception as e:
                print(f"Error processing product {product_id}: {e}")
                save_error_id(product_id)  
        if batch_results:
            save_to_json_batch(batch_results)
    return results

if __name__ == "__main__":
    df = pd.read_csv('products-0-200000.csv')
    ids = get_Id(df)
    results = info_products(ids, max_workers=20)
