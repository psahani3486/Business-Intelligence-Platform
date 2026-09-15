from backend.database import get_db_connection

def create_ml_features():
    """Generates feature tables for ML models (CLV, Churn, Forecasting)."""
    print("Generating ML feature tables...")
    with get_db_connection() as conn:
        
        # 1. CLV Features (Customer Lifetime Value)
        # RFM (Recency, Frequency, Monetary) for each unique customer
        print("Creating features_clv...")
        conn.execute("DROP TABLE IF EXISTS features_clv")
        conn.execute("""
            CREATE TABLE features_clv AS
            WITH customer_orders AS (
                SELECT 
                    c.customer_unique_id,
                    f.order_id,
                    f.purchase_timestamp,
                    f.total_item_value
                FROM fact_order_items f
                JOIN dim_customers c ON f.customer_id = c.customer_id
            ),
            rfm AS (
                SELECT
                    customer_unique_id,
                    MAX(purchase_timestamp) as last_purchase_date,
                    COUNT(DISTINCT order_id) as total_orders,
                    SUM(total_item_value) as total_spend,
                    AVG(total_item_value) as avg_order_value,
                    DATE_DIFF('day', MAX(purchase_timestamp), (SELECT MAX(purchase_timestamp) FROM customer_orders)) as recency_days
                FROM customer_orders
                GROUP BY 1
            )
            SELECT * FROM rfm
        """)

        # 2. Time Series Features for Forecasting
        # Daily revenue with lag features
        print("Creating features_forecasting...")
        conn.execute("DROP TABLE IF EXISTS features_forecasting")
        conn.execute("""
            CREATE TABLE features_forecasting AS
            WITH daily_revenue AS (
                SELECT 
                    DATE_TRUNC('day', purchase_timestamp) as ds,
                    SUM(price) as y
                FROM fact_order_items
                GROUP BY 1
            )
            SELECT 
                ds,
                y,
                LAG(y, 1) OVER (ORDER BY ds) as lag_1,
                LAG(y, 7) OVER (ORDER BY ds) as lag_7,
                LAG(y, 30) OVER (ORDER BY ds) as lag_30,
                EXTRACT(dow FROM ds) as day_of_week,
                EXTRACT(month FROM ds) as month
            FROM daily_revenue
            ORDER BY ds
        """)
        
        # 3. Features for Inventory Forecasting (Daily Units Sold)
        print("Creating features_inventory...")
        conn.execute("DROP TABLE IF EXISTS features_inventory")
        conn.execute("""
            CREATE TABLE features_inventory AS
            WITH daily_units AS (
                SELECT 
                    DATE_TRUNC('day', purchase_timestamp) as ds,
                    COUNT(order_item_id) as y
                FROM fact_order_items
                GROUP BY 1
            )
            SELECT 
                ds,
                y,
                LAG(y, 1) OVER (ORDER BY ds) as lag_1,
                LAG(y, 7) OVER (ORDER BY ds) as lag_7,
                EXTRACT(dow FROM ds) as day_of_week
            FROM daily_units
            ORDER BY ds
        """)

        # 4. Features for Customer Growth Forecasting
        print("Creating features_customer_metrics_daily...")
        conn.execute("DROP TABLE IF EXISTS features_customer_metrics_daily")
        conn.execute("""
            CREATE TABLE features_customer_metrics_daily AS
            WITH customer_first_purchase AS (
                SELECT 
                    customer_unique_id,
                    MIN(DATE_TRUNC('day', purchase_timestamp)) as first_date
                FROM fact_order_items f
                JOIN dim_customers c ON f.customer_id = c.customer_id
                GROUP BY 1
            ),
            daily_orders AS (
                SELECT 
                    DATE_TRUNC('day', f.purchase_timestamp) as ds,
                    c.customer_unique_id,
                    MIN(cfp.first_date) as first_date
                FROM fact_order_items f
                JOIN dim_customers c ON f.customer_id = c.customer_id
                JOIN customer_first_purchase cfp ON c.customer_unique_id = cfp.customer_unique_id
                GROUP BY 1, 2
            ),
            daily_metrics AS (
                SELECT 
                    ds,
                    COUNT(DISTINCT CASE WHEN ds = first_date THEN customer_unique_id END) as new_customers,
                    COUNT(DISTINCT CASE WHEN ds > first_date THEN customer_unique_id END) as returning_customers,
                    COUNT(DISTINCT customer_unique_id) as dau
                FROM daily_orders
                GROUP BY 1
            ),
            daily_metrics_with_mau AS (
                SELECT 
                    ds,
                    new_customers,
                    returning_customers,
                    dau,
                    SUM(dau) OVER (ORDER BY ds ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as mau
                FROM daily_metrics
            )
            SELECT 
                ds,
                new_customers,
                returning_customers,
                dau,
                mau,
                COALESCE((mau - LAG(mau, 1) OVER (ORDER BY ds)) * 100.0 / NULLIF(LAG(mau, 1) OVER (ORDER BY ds), 0), 0) as growth_rate,
                LAG(new_customers, 1) OVER (ORDER BY ds) as lag_1_new,
                LAG(returning_customers, 1) OVER (ORDER BY ds) as lag_1_returning,
                LAG(dau, 1) OVER (ORDER BY ds) as lag_1_dau,
                LAG(new_customers, 7) OVER (ORDER BY ds) as lag_7_new,
                LAG(returning_customers, 7) OVER (ORDER BY ds) as lag_7_returning,
                EXTRACT(dow FROM ds) as day_of_week
            FROM daily_metrics_with_mau
            ORDER BY ds
        """)
        
        # 5. Features for Order Anomalies (Daily Order Count)
        print("Creating features_orders_daily...")
        conn.execute("DROP TABLE IF EXISTS features_orders_daily")
        conn.execute("""
            CREATE TABLE features_orders_daily AS
            WITH daily_orders AS (
                SELECT 
                    DATE_TRUNC('day', purchase_timestamp) as ds,
                    COUNT(DISTINCT order_id) as y
                FROM fact_order_items
                GROUP BY 1
            )
            SELECT 
                ds,
                y,
                LAG(y, 1) OVER (ORDER BY ds) as lag_1,
                LAG(y, 7) OVER (ORDER BY ds) as lag_7,
                EXTRACT(dow FROM ds) as day_of_week
            FROM daily_orders
            ORDER BY ds
        """)

        # 6. Features for Fraud Anomalies (Daily canceled orders & high freight values)
        # Note: We don't have 'canceled' easily in fact_order_items if it's pre-filtered, 
        # but let's assume we can just use freight anomalies or count of extreme freight values
        print("Creating features_fraud_daily...")
        conn.execute("DROP TABLE IF EXISTS features_fraud_daily")
        conn.execute("""
            CREATE TABLE features_fraud_daily AS
            WITH daily_fraud AS (
                SELECT 
                    DATE_TRUNC('day', purchase_timestamp) as ds,
                    SUM(CASE WHEN freight_value > 50 THEN 1 ELSE 0 END) as y,
                    AVG(freight_value) as freight
                FROM fact_order_items
                GROUP BY 1
            )
            SELECT 
                ds,
                y,
                freight,
                LAG(y, 1) OVER (ORDER BY ds) as lag_1,
                LAG(y, 7) OVER (ORDER BY ds) as lag_7,
                EXTRACT(dow FROM ds) as day_of_week
            FROM daily_fraud
            ORDER BY ds
        """)
        
        # 7. Telco Churn Features are mostly ready in the raw table,

    print("ML feature engineering complete.")

def run():
    create_ml_features()

if __name__ == "__main__":
    run()
