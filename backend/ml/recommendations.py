import pandas as pd
import mlflow
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from backend.database import execute_query
import joblib
import os

def train_recommendation_model():
    """Builds an item-based collaborative filtering matrix."""
    print("Building Recommendation Engine...")
    
    # Get order items to find co-purchases
    # For a real system we'd use sparse matrices, but for this demo with Olist 
    # we'll restrict to top 1000 products by volume to keep memory reasonable.
    
    query = """
        WITH top_products AS (
            SELECT product_id, COUNT(*) as cnt
            FROM fact_order_items
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT 500
        )
        SELECT f.order_id, f.product_id
        FROM fact_order_items f
        JOIN top_products t ON f.product_id = t.product_id
    """
    
    df = execute_query(query)
    
    if df is None or len(df) == 0:
        print("Error: No data found for recommendations")
        return None
        
    # Create a user-item matrix (order_id as proxy for basket/user session)
    # 1 if purchased in that order, 0 otherwise
    basket = pd.crosstab(df['order_id'], df['product_id'])
    # Convert to 1s and 0s
    basket = (basket > 0).astype(int)
    
    with mlflow.start_run(run_name="product_recommendations"):
        # Calculate item similarity matrix
        item_similarity = cosine_similarity(basket.T)
        similarity_df = pd.DataFrame(
            item_similarity, 
            index=basket.columns, 
            columns=basket.columns
        )
        
        # Log some basic metrics
        mlflow.log_metric("num_products_indexed", len(similarity_df))
        
        print(f"Recommendation Engine Built for {len(similarity_df)} products.")
        
        # Save the similarity matrix
        os.makedirs(os.path.join(os.path.dirname(__file__), 'artifacts'), exist_ok=True)
        model_path = os.path.join(os.path.dirname(__file__), 'artifacts/item_similarity.joblib')
        joblib.dump(similarity_df, model_path)
        
        # Log artifact to MLflow
        mlflow.log_artifact(model_path, "recommendation_matrix")
        
    return similarity_df

if __name__ == "__main__":
    train_recommendation_model()
