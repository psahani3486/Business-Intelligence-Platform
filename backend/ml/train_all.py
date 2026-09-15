import os
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)
import mlflow
import time
from backend.ml import forecasting, churn, clv, anomaly, recommendations, clustering, advanced_forecasting

def run_all_training():
    print("="*50)
    print("Starting ML Model Training Pipeline")
    print("="*50)
    
    # Set MLflow tracking URI
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("BI_Platform_Models")
    
    start_time = time.time()
    
    try:
        # 1. Forecasting (XGBoost)
        forecasting.train_forecasting_model()
        advanced_forecasting.train_inventory_model()
        advanced_forecasting.train_customer_growth_models()
        
        # 2. Churn
        churn.train_churn_model()
        
        # 3. CLV
        clv.train_clv_model()
        
        # 4. Anomaly Detection
        anomaly.train_all_anomaly_models()
        
        # 5. Recommendations
        recommendations.train_recommendation_model()

        # 6. Clustering
        clustering.train_clustering_model()
        
        elapsed = time.time() - start_time
        print("="*50)
        print(f"All models trained successfully in {elapsed:.2f} seconds.")
        print("="*50)
        
    except Exception as e:
        print("="*50)
        print(f"Model training failed: {e}")
        print("="*50)

if __name__ == "__main__":
    run_all_training()
