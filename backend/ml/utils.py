import mlflow
from mlflow.tracking import MlflowClient
import os

def get_latest_model(model_artifact_name: str, experiment_name: str = "BI_Platform_Models"):
    """
    Retrieves the latest model logged in MLflow for the given experiment and artifact name.
    """
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()
    
    experiment = client.get_experiment_by_name(experiment_name)
    if not experiment:
        return None
        
    # Search for runs, we need to inspect them or just filter by run name if possible. 
    # Since we can't easily filter by artifact, let's get top 50 and find the first one with the artifact.
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=50
    )
    
    model_uri = None
    for run in runs:
        # Check if artifact exists in this run
        artifacts = [a.path for a in client.list_artifacts(run.info.run_id)]
        if model_artifact_name in artifacts:
            model_uri = f"runs:/{run.info.run_id}/{model_artifact_name}"
            break
            
    if not model_uri:
        return None
        
    try:
        # We can use pyfunc to load any model flavor generically
        model = mlflow.pyfunc.load_model(model_uri)
        return model
    except Exception as e:
        print(f"Error loading model {model_artifact_name}: {e}")
        return None
