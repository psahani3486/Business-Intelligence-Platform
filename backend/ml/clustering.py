import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import mlflow
import os
from backend.database import execute_query

def train_clustering_model():
    """Trains a K-Means clustering model for customer segmentation."""
    print("Training Customer Cohort Clustering Model...")
    
    # Set MLflow environment
    mlflow.set_tracking_uri("./mlruns")
    mlflow.set_experiment("BI_Platform_Models")
    
    # We will cluster based on recency, frequency, monetary (RFM) + review score if possible
    # Get features from DuckDB
    query = """
        SELECT 
            customer_unique_id, 
            total_orders as frequency, 
            avg_order_value, 
            recency_days,
            total_spend as monetary
        FROM features_clv
    """
    df = execute_query(query)
    
    if df is None or len(df) == 0:
        print("Error: No data found in features_clv for clustering")
        return None
        
    df = df.dropna()
    features = ['frequency', 'recency_days', 'monetary']
    X = df[features].copy()
    
    # K-Means requires scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    with mlflow.start_run(run_name="customer_clustering"):
        # We will aim for 4 distinct cohorts
        kmeans = KMeans(n_clusters=4, random_state=42, n_init="auto")
        
        mlflow.log_params(kmeans.get_params())
        
        # Fit and predict
        clusters = kmeans.fit_predict(X_scaled)
        
        # Calculate and log silhouette score
        from sklearn.metrics import silhouette_score
        try:
            score = silhouette_score(X_scaled, clusters)
            mlflow.log_metric("silhouette_score", score)
        except Exception as e:
            print(f"Could not calculate silhouette score: {e}")
        
        # Log model
        # We also need the scaler for inference. We can create a pipeline.
        from sklearn.pipeline import Pipeline
        pipeline = Pipeline([
            ('scaler', scaler),
            ('kmeans', kmeans)
        ])
        
        mlflow.sklearn.log_model(pipeline, "clustering_model")
        
        print("Clustering Model Trained and Logged.")
        
    return pipeline

if __name__ == "__main__":
    train_clustering_model()
