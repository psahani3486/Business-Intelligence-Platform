import pandas as pd
import numpy as np
import shap
import os
import joblib
from fastapi import APIRouter
from typing import List
from backend.api.schemas import ChurnPrediction
from backend.database import execute_query
from backend.ml.utils import get_latest_model

router = APIRouter()

_churn_model = None
_label_encoders = None

def get_churn_model_and_encoders():
    global _churn_model, _label_encoders
    if _churn_model is None:
        _churn_model = get_latest_model("churn_model")
        
    if _label_encoders is None:
        enc_path = os.path.join(os.path.dirname(__file__), '../../ml/artifacts/churn_encoders.joblib')
        if os.path.exists(enc_path):
            _label_encoders = joblib.load(enc_path)
            
    return _churn_model, _label_encoders

@router.get("/predictions", response_model=List[ChurnPrediction])
def get_churn_predictions():
    """Get top customers at risk of churning."""
    model, encoders = get_churn_model_and_encoders()
    
    query = "SELECT * FROM telco_churn"
    df = execute_query(query)
    
    if df is None or len(df) == 0:
        return []
        
    # If model is not available, fallback to mock data
    if model is None or encoders is None:
        predictions = []
        for _, row in df.head(10).iterrows():
            import random
            risk = random.uniform(0.1, 0.95)
            pred_class = "High Risk" if risk > 0.7 else "Medium Risk" if risk > 0.4 else "Low Risk"
            predictions.append(ChurnPrediction(
                customer_id=str(row['customerid']),
                risk_score=float(risk),
                prediction=pred_class,
                top_factors=[
                    {"name": "Tenure", "value": float(row['tenure_months'])},
                    {"name": "Monthly Charges", "value": float(row['monthly_charges'])}
                ]
            ))
        predictions.sort(key=lambda x: x.risk_score, reverse=True)
        return predictions

    # Preprocessing
    cols_to_drop = ['customerid', 'count', 'country', 'state', 'city', 'zip_code', 'lat_long', 'latitude', 'longitude', 'churn_label', 'churn_score', 'cltv', 'churn_reason']
    features = [c for c in df.columns if c not in cols_to_drop and c != 'churn_value']
    
    X = df[features].copy()
    customer_ids = df['customerid'].values
    
    for col, le in encoders.items():
        if col in X.columns:
            X[col] = X[col].astype(str)
            # Handle unseen labels by mapping them to an unknown class or the most frequent class
            # Since this is a demo, we will use a safe transform
            X[col] = X[col].map(lambda s: s if s in le.classes_ else le.classes_[0])
            X[col] = le.transform(X[col])
            
    # Predict probabilities
    try:
        xgb_model = model.unwrap_python_model() # Get underlying XGBoost model if pyfunc
    except:
        xgb_model = model

    # If it's a PyFunc model wrapper, predict might not support predict_proba directly on the wrapper in all mlflow versions
    # so we extract the underlying model if possible, or just use the model object
    if hasattr(model, '_model_impl'):
        xgb_model = model._model_impl.xgb_model
        
    # Predict probabilities (assuming the model has predict_proba)
    # Using the pyfunc model directly if unwrap doesn't give us the XGB model
    try:
        if hasattr(xgb_model, 'predict_proba'):
            probs = xgb_model.predict_proba(X)[:, 1]
        else:
            # For pyfunc, predict often returns probabilities for classification if trained with predict_proba
            # Let's try raw predict
            probs = model.predict(X)
            if len(probs.shape) > 1 and probs.shape[1] > 1:
                probs = probs[:, 1]
    except Exception as e:
        print(f"Error predicting: {e}")
        return []

    # Get top 20 at risk
    top_indices = np.argsort(probs)[::-1][:20]
    
    # Calculate SHAP values for the top 20
    X_top = X.iloc[top_indices]
    try:
        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(X_top)
    except:
        shap_values = None
        
    predictions = []
    for i, idx in enumerate(top_indices):
        risk = float(probs[idx])
        pred_class = "High Risk" if risk > 0.7 else "Medium Risk" if risk > 0.4 else "Low Risk"
        
        top_factors = []
        if shap_values is not None:
            # Get top 2 features driving churn for this specific customer
            customer_shap = shap_values[i]
            top_feature_indices = np.argsort(np.abs(customer_shap))[::-1][:2]
            for f_idx in top_feature_indices:
                feat_name = features[f_idx]
                feat_val = df.iloc[idx][feat_name]
                top_factors.append({"name": feat_name, "value": float(feat_val) if isinstance(feat_val, (int, float)) else str(feat_val)})
        else:
            # Fallback if SHAP fails
            top_factors = [
                {"name": "Tenure", "value": float(df.iloc[idx]['tenure_months'])},
                {"name": "Monthly Charges", "value": float(df.iloc[idx]['monthly_charges'])}
            ]
            
        predictions.append(ChurnPrediction(
            customer_id=str(customer_ids[idx]),
            risk_score=risk,
            prediction=pred_class,
            top_factors=top_factors
        ))
        
    return predictions
