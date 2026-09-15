from backend.database import get_db_connection

def transform_olist_data():
    """Cleans and joins the raw Olist data into analytics-ready fact/dim tables."""
    print("Transforming Olist data...")
    with get_db_connection() as conn:
        
        # 1. Create a clean date dimension (optional but good practice)
        # For simplicity, we'll cast timestamps in the fact table.

        # 2. Create translated product dimension
        print("Creating dim_products...")
        conn.execute("DROP TABLE IF EXISTS dim_products")
        conn.execute("""
            CREATE TABLE dim_products AS
            SELECT 
                p.product_id,
                COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') as category_name,
                p.product_weight_g,
                p.product_length_cm,
                p.product_height_cm,
                p.product_width_cm
            FROM olist_products p
            LEFT JOIN product_category_name_translation t 
                ON p.product_category_name = t.product_category_name
        """)

        # 3. Create customers dimension
        print("Creating dim_customers...")
        conn.execute("DROP TABLE IF EXISTS dim_customers")
        conn.execute("""
            CREATE TABLE dim_customers AS
            SELECT 
                customer_id,
                customer_unique_id,
                customer_zip_code_prefix as zip_code,
                customer_city as city,
                customer_state as state
            FROM olist_customers
        """)
        
        # 4. Create sellers dimension
        print("Creating dim_sellers...")
        conn.execute("DROP TABLE IF EXISTS dim_sellers")
        conn.execute("""
            CREATE TABLE dim_sellers AS
            SELECT 
                seller_id,
                seller_city as city,
                seller_state as state
            FROM olist_sellers
        """)

        # 5. Create core fact table (Orders + Items + Payments + Reviews)
        # Note: One order can have multiple items and multiple payments.
        # We will create an order-item level fact table.
        print("Creating fact_order_items...")
        conn.execute("DROP TABLE IF EXISTS fact_order_items")
        conn.execute("""
            CREATE TABLE fact_order_items AS
            SELECT 
                o.order_id,
                o.customer_id,
                i.order_item_id,
                i.product_id,
                i.seller_id,
                o.order_status,
                CAST(o.order_purchase_timestamp AS TIMESTAMP) as purchase_timestamp,
                CAST(o.order_delivered_customer_date AS TIMESTAMP) as delivered_timestamp,
                i.price,
                i.freight_value,
                (i.price * 0.7) as cost,
                (i.price * 0.3) as profit,
                (i.price + i.freight_value) as total_item_value
            FROM olist_orders o
            JOIN olist_order_items i ON o.order_id = i.order_id
            WHERE o.order_status = 'delivered'
        """)

        # 6. Aggregate monthly revenue for fast dashboard queries
        print("Creating agg_monthly_revenue...")
        conn.execute("DROP TABLE IF EXISTS agg_monthly_revenue")
        conn.execute("""
            CREATE TABLE agg_monthly_revenue AS
            SELECT 
                DATE_TRUNC('month', purchase_timestamp) as revenue_month,
                SUM(price) as total_revenue,
                SUM(cost) as total_cost,
                SUM(profit) as total_profit,
                SUM(freight_value) as total_freight,
                COUNT(DISTINCT order_id) as total_orders,
                COUNT(DISTINCT customer_id) as total_customers
            FROM fact_order_items
            GROUP BY 1
            ORDER BY 1
        """)
        
        # 7. Aggregate category performance
        print("Creating agg_category_performance...")
        conn.execute("DROP TABLE IF EXISTS agg_category_performance")
        conn.execute("""
            CREATE TABLE agg_category_performance AS
            SELECT 
                p.category_name,
                SUM(f.price) as total_revenue,
                COUNT(f.order_item_id) as units_sold
            FROM fact_order_items f
            JOIN dim_products p ON f.product_id = p.product_id
            GROUP BY 1
            ORDER BY 2 DESC
        """)

    print("Olist data transformation complete.")

def run():
    transform_olist_data()

if __name__ == "__main__":
    run()
