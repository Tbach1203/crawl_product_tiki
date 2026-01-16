import psycopg2
from config.config import load_config
from psycopg2.extras import execute_batch
import os
import json


def connect(config):
    try:
        conn = psycopg2.connect(**config)
        print('Connected to the PostgreSQL server.')
        return conn
    except psycopg2.OperationalError as e:
        print("❌ Cannot connect to database:", e)
    except Exception as e:
        print("❌ Unexpected error while connecting:", e)
    return None


def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS product (
        id BIGINT PRIMARY KEY,
        name TEXT,
        url_key TEXT,
        price DOUBLE PRECISION,
        description TEXT,
        images TEXT
    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("✅ Table product created/exists")
    except psycopg2.DatabaseError as e:
        conn.rollback()
        print("❌ Error creating table:", e)
    except Exception as e:
        conn.rollback()
        print("❌ Unexpected error creating table:", e)


def load_json_chunks(folder_path):
    products = []

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    for file_name in sorted(os.listdir(folder_path)):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, file_name)
        print(f"📂 Loading {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                if not isinstance(data, list):
                    raise ValueError("JSON content must be a list")

                products.extend(data)

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in {file_name}: {e}")
        except UnicodeDecodeError as e:
            print(f"❌ Encoding error in {file_name}: {e}")
        except ValueError as e:
            print(f"❌ Data format error in {file_name}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error reading {file_name}: {e}")

    return products


def insert_products(conn, products):
    if not products:
        print("⚠️ No products to insert")
        return

    sql = """
    INSERT INTO product (id, name, url_key, price, description, images)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING
    """

    values = [
        (
            p.get("id"),
            p.get("name"),
            p.get("url_key"),
            p.get("price"),
            p.get("description"),
            p.get("images")
        )
        for p in products
    ]

    try:
        with conn.cursor() as cur:
            execute_batch(cur, sql, values, page_size=500)
        conn.commit()
        print(f"✅ Inserted {len(values)} records")

    except psycopg2.DatabaseError as e:
        conn.rollback()
        print("❌ Database error during insert:", e)

    except Exception as e:
        conn.rollback()
        print("❌ Unexpected error during insert:", e)


if __name__ == '__main__':
    try:
        config = load_config()
        conn = connect(config)

        if conn is None:
            raise RuntimeError("Database connection failed")

        create_table(conn)

        products = load_json_chunks("product")
        insert_products(conn, products)

    except Exception as e:
        print("❌ Fatal error:", e)

    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("🔒 Database connection closed")
