import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import uuid
from backend.database import execute_query
from backend.ml.utils import get_latest_model

def get_temp_filepath():
    """Generates a temporary file path for chart images."""
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    return os.path.join(temp_dir, f"chart_{uuid.uuid4().hex[:8]}.png")

def generate_revenue_trend_chart() -> str:
    """Generates a chart of the last 30 days of revenue."""
    query = """
        SELECT ds, y 
        FROM features_forecasting 
        ORDER BY ds DESC 
        LIMIT 30
    """
    df = execute_query(query)
    
    if df is None or len(df) == 0:
        return None
        
    df = df.sort_values('ds')
    df['ds'] = pd.to_datetime(df['ds'])
    
    plt.figure(figsize=(8, 4))
    plt.plot(df['ds'], df['y'], color='#3B82F6', linewidth=2, marker='o', markersize=4)
    plt.fill_between(df['ds'], df['y'], color='#3B82F6', alpha=0.1)
    
    plt.title('30-Day Revenue Trend', fontsize=12, pad=10)
    plt.ylabel('Revenue ($)', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Format x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    filepath = get_temp_filepath()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath

def generate_forecast_chart() -> str:
    """Generates a chart of the next 30 days forecast (using XGBoost logic)."""
    model = get_latest_model("forecasting_model")
    
    query = """
        SELECT ds, y, lag_1, lag_7, lag_30, day_of_week, month 
        FROM features_forecasting 
        ORDER BY ds DESC 
        LIMIT 30
    """
    df = execute_query(query)
    
    if df is None or len(df) == 0 or model is None:
        return None
        
    df = df.sort_values('ds').reset_index(drop=True)
    last_date = pd.to_datetime(df['ds'].iloc[-1])
    
    # Predict next 14 days for simplicity in chart
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 15)]
    future_df = pd.DataFrame({'ds': future_dates})
    future_df['day_of_week'] = future_df['ds'].dt.dayofweek
    future_df['month'] = future_df['ds'].dt.month
    
    # Simple naive lag estimation for plotting
    last_y = df['y'].iloc[-1]
    future_df['lag_1'] = last_y
    future_df['lag_7'] = last_y
    future_df['lag_30'] = last_y
    
    features = ['lag_1', 'lag_7', 'lag_30', 'day_of_week', 'month']
    X_future = future_df[features].fillna(0)
    
    try:
        preds = model.predict(X_future)
        future_df['predicted_y'] = preds
        
        plt.figure(figsize=(8, 4))
        
        # Plot historical
        hist_dates = pd.to_datetime(df['ds'].tail(14))
        hist_y = df['y'].tail(14)
        plt.plot(hist_dates, hist_y, color='#6B7280', linewidth=2, label='Historical')
        
        # Plot forecast
        plt.plot(future_df['ds'], future_df['predicted_y'], color='#10B981', linewidth=2, linestyle='--', marker='o', markersize=4, label='Forecast')
        
        plt.title('14-Day Revenue Forecast', fontsize=12, pad=10)
        plt.ylabel('Revenue ($)', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filepath = get_temp_filepath()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    except Exception as e:
        print(f"Error generating forecast chart: {e}")
        return None
