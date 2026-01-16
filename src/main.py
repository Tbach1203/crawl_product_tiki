from etl.crawl_tiki_products import get_Id, info_products
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("data\input\products-0-200000.csv")
    ids = get_Id(df)
    info_products(ids, max_workers=20)