import pandas as pd
import requests
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
}

def get_Id(df):
    return df['id'].tolist()

def product():
    pass

def info_Products(ids):
    result = []
    for id in range(len(ids)):
        response = requests.get(url='https://api.tiki.vn/product-detail/api/v1/products/{}'.format(ids[id]), headers=headers, timeout=10)
        if response.status_code == 200:
            result.append(response.json())
            # time.sleep(2)
    return result
        
if __name__ == "__main__":
    df = pd.read_csv('products-0-200000.csv')
    ids = get_Id(df)
    # print(df[:10])
    products_tiki = info_Products(ids[:10])
    # print(products_tiki)
    with open('products.json', 'w', encoding='utf-8') as file:
        json.dump(products_tiki, file, indent=4)
    


    
    
