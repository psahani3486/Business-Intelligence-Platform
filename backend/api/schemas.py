from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class KPIData(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    avg_order_value: float
    revenue_growth_pct: float
    total_profit: float
    margin_pct: float

class ChartDataPoint(BaseModel):
    name: str
    value: float
    secondary_value: Optional[float] = None

class NLQRequest(BaseModel):
    question: str

class NLQResponse(BaseModel):
    question: str
    sql: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ChurnPrediction(BaseModel):
    customer_id: str
    risk_score: float
    prediction: str
    top_factors: List[Dict[str, Any]]

class CustomerGrowthDataPoint(BaseModel):
    ds: str
    new_customers: float
    returning_customers: float
    mau: float
    growth_rate: float

class CustomerGrowthForecastResponse(BaseModel):
    xgboost: List[CustomerGrowthDataPoint]
    prophet: List[CustomerGrowthDataPoint]
    metrics: Dict[str, Any]

class DiscountRecommendation(BaseModel):
    product_id: str
    product_name: str
    discount_percentage: int
    target_segment: str
    reason: str

class EmailAudience(BaseModel):
    segment_name: str
    customer_count: int
    recommended_action: str
    open_rate_estimate: str

class CrossSellRecommendation(BaseModel):
    base_product_id: str
    recommended_product_id: str
    recommended_product_name: str
    reason: str
    score: float

class UpSellRecommendation(BaseModel):
    base_product_id: str
    premium_product_id: str
    premium_product_name: str
    additional_margin: float
    score: float

class CustomerTargeting(BaseModel):
    customer_id: str
    segment: str
    recommended_campaign: str
    churn_risk: str
    recommended_products: List[Dict[str, Any]]

class AnomalyAlert(BaseModel):
    date: str
    metric_type: str
    value: float
    severity: str
    message: str

class InventoryItemForecast(BaseModel):
    product_id: str
    product_category: str
    inventory_demand: float
    safety_stock: float
    reorder_quantity: float
    expected_stockout_date: str
    current_stock: float

class InventoryForecastResponse(BaseModel):
    items: List[InventoryItemForecast]
    summary: Dict[str, Any]

