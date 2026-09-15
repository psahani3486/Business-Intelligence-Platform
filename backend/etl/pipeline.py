import time
from backend.etl import load_raw, transform, feature_engineering

def run_pipeline():
    print("="*50)
    print("Starting Data Pipeline")
    print("="*50)
    
    start_time = time.time()
    
    try:
        # Step 1: Load raw data
        load_raw.run()
        
        # Step 2: Transform and create analytical tables
        transform.run()
        
        # Step 3: Feature engineering for ML
        feature_engineering.run()
        
        elapsed = time.time() - start_time
        print("="*50)
        print(f"Pipeline completed successfully in {elapsed:.2f} seconds.")
        print("="*50)
        
    except Exception as e:
        print("="*50)
        print(f"Pipeline failed: {e}")
        print("="*50)

if __name__ == "__main__":
    run_pipeline()
