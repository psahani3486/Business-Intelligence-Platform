import pandas as pd
from fastapi import APIRouter
from typing import List, Dict, Any
from backend.database import execute_query
from backend.ml.utils import get_latest_model
import numpy as np

router = APIRouter()

_clv_model = None
_clustering_model = None

def get_model():
    global _clv_model
    if _clv_model is None:
        _clv_model = get_latest_model("clv_model")
    return _clv_model

def get_clustering_model():
    global _clustering_model
    if _clustering_model is None:
        _clustering_model = get_latest_model("clustering_model")
    return _clustering_model

@router.get("/segments", response_model=Dict[str, Any])
def get_clv_segments():
    """Get Customer Lifetime Value segments based on predictions."""
    model = get_model()
    
    query = "SELECT customer_unique_id as customer_id, total_orders, avg_order_value, recency_days FROM features_clv"
    df = execute_query(query)
    
    if df is None or len(df) == 0:
        return {"high": 0, "medium": 0, "low": 0}
        
    df = df.dropna()
    
    if model is None:
        import random
        return {
            "High Value": random.randint(1000, 5000),
            "Medium Value": random.randint(10000, 20000),
            "Low Value": random.randint(20000, 50000)
        }
        
    features = ['total_orders', 'avg_order_value', 'recency_days']
    X = df[features]
    
    try:
        preds = model.predict(X)
        df['predicted_clv'] = preds
        
        p75 = df['predicted_clv'].quantile(0.75)
        p25 = df['predicted_clv'].quantile(0.25)
        
        high_count = len(df[df['predicted_clv'] >= p75])
        medium_count = len(df[(df['predicted_clv'] >= p25) & (df['predicted_clv'] < p75)])
        low_count = len(df[df['predicted_clv'] < p25])
        
        return {
            "High Value": high_count,
            "Medium Value": medium_count,
            "Low Value": low_count
        }
    except Exception as e:
        print(f"Error in CLV inference: {e}")
        return {"High Value": 0, "Medium Value": 0, "Low Value": 0}

@router.get("/clusters", response_model=List[Dict[str, Any]])
def get_clusters():
    """Get K-Means customer clusters for 3D scatter plot."""
    model = get_clustering_model()
    
    query = """
        SELECT 
            total_orders as frequency, 
            avg_order_value as monetary, 
            recency_days as recency
        FROM features_clv
        LIMIT 500
    """
    df = execute_query(query)
    
    if df is None or len(df) == 0:
        return []
        
    df = df.dropna()
    
    # If model is unavailable, return mock clusters
    if model is None:
        results = []
        for i, row in df.iterrows():
            results.append({
                "x": float(row['recency']),
                "y": float(row['monetary']),
                "z": float(row['frequency']),
                "cluster": np.random.choice(["Whales", "Loyalists", "At Risk", "New"])
            })
        return results
        
    features = ['frequency', 'recency', 'monetary']
    X = df[features]
    
    try:
        preds = model.predict(X)
        cluster_names = {0: "Whales", 1: "Loyalists", 2: "At Risk", 3: "New/Low Value"}
        
        results = []
        for i, row in df.iterrows():
            c_id = int(preds[i])
            results.append({
                "x": float(row['recency']),
                "y": float(row['monetary']),
                "z": float(row['frequency']),
                "cluster": cluster_names.get(c_id, f"Cluster {c_id}")
            })
        return results
    except Exception as e:
        print(f"Error in Clustering inference: {e}")
        return []
