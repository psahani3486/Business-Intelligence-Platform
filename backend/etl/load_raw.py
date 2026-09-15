import os
import pandas as pd
from backend.database import get_db_connection

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))

CSV_FILES = {
    'olist_customers': 'olist_customers_dataset.csv',
    'olist_order_items': 'olist_order_items_dataset.csv',
    'olist_order_payments': 'olist_order_payments_dataset.csv',
    'olist_order_reviews': 'olist_order_reviews_dataset.csv',
    'olist_orders': 'olist_orders_dataset.csv',
    'olist_products': 'olist_products_dataset.csv',
    'olist_sellers': 'olist_sellers_dataset.csv',
    'product_category_name_translation': 'product_category_name_translation.csv'
}

def load_csvs_to_duckdb():
    print("Loading raw CSV files into DuckDB...")
    with get_db_connection() as conn:
        for table_name, file_name in CSV_FILES.items():
            file_path = os.path.join(DATA_DIR, file_name)
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} not found. Skipping {table_name}.")
                continue
            
            print(f"Loading {file_name} into table {table_name}...")
            # Use DuckDB's native CSV reader for performance
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} AS 
                SELECT * FROM read_csv_auto('{file_path}')
            """)
            # If the table already exists, we might want to replace it in a fresh pipeline run.
            # For simplicity in this demo, we'll drop and recreate if it exists.
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{file_path}', ignore_errors=true)
            """)
    print("CSV loading complete.")

def load_excel_to_duckdb():
    print("Loading Telco Churn Excel file into DuckDB...")
    file_path = os.path.join(DATA_DIR, 'Telco_customer_churn.xlsx')
    
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found. Skipping telco_churn.")
        return

    # Use pandas to read Excel, then load DataFrame into DuckDB
    try:
        df = pd.read_excel(file_path)
        # Clean column names (remove spaces)
        df.columns = [c.replace(' ', '_').lower() for c in df.columns]
        
        with get_db_connection() as conn:
            conn.execute("DROP TABLE IF EXISTS telco_churn")
            # DuckDB can automatically query Pandas DataFrames in the local scope
            conn.execute("CREATE TABLE telco_churn AS SELECT * FROM df")
        print("Excel loading complete.")
    except Exception as e:
        print(f"Error loading Excel file: {e}")

def run():
    load_csvs_to_duckdb()
    load_excel_to_duckdb()

if __name__ == "__main__":
    run()
