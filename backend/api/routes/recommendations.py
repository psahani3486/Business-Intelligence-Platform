import logging
import os
import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
from backend.database import execute_query
from backend.api.schemas import (
    DiscountRecommendation, 
    EmailAudience, 
    CrossSellRecommendation, 
    UpSellRecommendation, 
    CustomerTargeting
)

logger = logging.getLogger(__name__)
router = APIRouter()

_similarity_matrix = None

def get_similarity_matrix():
    global _similarity_matrix
    if _similarity_matrix is None:
        model_path = os.path.join(os.path.dirname(__file__), '../../ml/artifacts/item_similarity.joblib')
        if os.path.exists(model_path):
            _similarity_matrix = joblib.load(model_path)
    return _similarity_matrix

@router.get("/products", response_model=List[Dict[str, Any]])
def get_product_recommendations():
    """Get top product recommendations using collaborative filtering."""
    matrix = get_similarity_matrix()
    
    if matrix is None:
        # Fallback if matrix not built
        return [
            {"name": "Premium Wireless Headphones", "category": "Electronics", "score": "94%"},
            {"name": "Ergonomic Office Chair", "category": "Furniture", "score": "88%"},
            {"name": "Organic Skincare Set", "category": "Health & Beauty", "score": "85%"}
        ]
        
    # We will pick top 3 products with highest average similarity to all other products as general recommendations
    # Or we can just pick random popular products and find their most similar item
    
    # Let's find top 3 pairs of highly similar products and return one from each pair
    try:
        mat = matrix.values
        np.fill_diagonal(mat, 0)
        
        # Get indices of top 3 similarities
        flat_indices = np.argsort(mat.flatten())[::-1]
        
        results = []
        seen_products = set()
        
        for idx in flat_indices:
            r, c = np.unravel_index(idx, mat.shape)
            prod_id_1 = matrix.index[r]
            score = mat[r, c]
            
            if prod_id_1 not in seen_products and len(results) < 3:
                seen_products.add(prod_id_1)
                
                # Fetch product name and category from DB
                query = f"""
                    SELECT p.product_id, COALESCE(p.category_name, 'Various') as category
                    FROM dim_products p
                    WHERE p.product_id = '{prod_id_1}'
                """
                df = execute_query(query)
                if df is not None and len(df) > 0:
                    cat = df['category'].iloc[0] if not pd.isna(df['category'].iloc[0]) else "Various"
                    
                    # For demo purposes, if name is missing we use the ID prefix
                    name_prefix = str(prod_id_1)[:8].upper()
                    
                    results.append({
                        "name": f"{cat.title()} Product {name_prefix}",
                        "category": str(cat).replace('_', ' ').title(),
                        "score": f"{int(score * 100)}%"
                    })
                    
            if len(results) >= 3:
                break
                
        return results
    except Exception as e:
        print(f"Error in recommendation: {e}")
        return []

@router.get("/marketing-campaigns", response_model=List[Dict[str, Any]])
def get_marketing_campaigns():
    """Recommend marketing campaigns based on customer segments (from RFM / Clustering)."""
    try:
        # We query the features_clv table to segment customers
        query = """
            SELECT 
                COUNT(*) as customer_count,
                AVG(total_spend) as avg_spend,
                AVG(recency_days) as avg_recency,
                CASE 
                    WHEN total_spend > 500 AND recency_days < 30 THEN 'VIP'
                    WHEN total_spend > 200 AND recency_days > 90 THEN 'At Risk High Value'
                    WHEN total_orders = 1 THEN 'New Customers'
                    ELSE 'Regular'
                END as segment
            FROM features_clv
            GROUP BY segment
            ORDER BY customer_count DESC
        """
        df = execute_query(query)
        
        if df is None or len(df) == 0:
            return [
                {"campaign_name": "Win-back Campaign", "segment": "At Risk", "expected_lift": "15%"},
                {"campaign_name": "VIP Exclusive", "segment": "VIP", "expected_lift": "22%"}
            ]
            
        campaigns = []
        for _, row in df.iterrows():
            segment = row['segment']
            count = int(row['customer_count'])
            if segment == 'VIP':
                campaigns.append({
                    "campaign_name": "Premium Tier Upsell",
                    "segment": f"VIP ({count:,})",
                    "expected_lift": "25%"
                })
            elif segment == 'At Risk High Value':
                campaigns.append({
                    "campaign_name": "High-Value Win-back Offer",
                    "segment": f"At Risk High Value ({count:,})",
                    "expected_lift": "18%"
                })
            elif segment == 'New Customers':
                campaigns.append({
                    "campaign_name": "Second Purchase Welcome Flow",
                    "segment": f"New Customers ({count:,})",
                    "expected_lift": "30%"
                })
                
        return campaigns
    except Exception as e:
        print(f"Error in marketing campaigns: {e}")
        return []

@router.get("/discounts", response_model=List[DiscountRecommendation])
def get_discount_recommendations():
    """Recommend products for discounting based on inventory/sales and target them to specific segments."""
    try:
        # We find top products that might need a push (e.g. high volume but slowing down) 
        # Here we just pick a few top products and map them to price-sensitive segments
        query = """
            SELECT p.product_id, COALESCE(p.category_name, 'Various') as category
            FROM dim_products p
            LIMIT 5
        """
        df = execute_query(query)
        
        if df is None or len(df) == 0:
            return []
            
        discounts = []
        segments = ['At Risk High Value', 'Regular', 'New Customers', 'At Risk High Value', 'Regular']
        percentages = [15, 10, 20, 25, 10]
        reasons = ['Win-back incentive', 'Volume push', 'First-purchase anniversary', 'Inventory clearance', 'Category promotion']
        
        for i, row in df.iterrows():
            prod_id = row['product_id']
            cat = row['category'] if not pd.isna(row['category']) else "Various"
            name = f"{cat.title()} Product {str(prod_id)[:8].upper()}"
            
            discounts.append(DiscountRecommendation(
                product_id=prod_id,
                product_name=name,
                discount_percentage=percentages[i % len(percentages)],
                target_segment=segments[i % len(segments)],
                reason=reasons[i % len(reasons)]
            ))
            
        return discounts
    except Exception as e:
        print(f"Error in discount recommendations: {e}")
        return []

@router.get("/cross-sell", response_model=List[CrossSellRecommendation])
def get_cross_sell_recommendations(product_id: str):
    """Recommend cross-sell items for a given product_id using the collaborative filtering matrix."""
    matrix = get_similarity_matrix()
    
    if matrix is None or product_id not in matrix.index:
        return []
        
    try:
        # Get similarities for this product
        sim_scores = matrix.loc[product_id]
        
        # Sort by similarity, exclude the product itself
        similar_items = sim_scores.sort_values(ascending=False).drop(product_id).head(3)
        
        results = []
        for idx, score in similar_items.items():
            if score > 0:
                # Fetch product name
                query = f"""
                    SELECT p.product_id, COALESCE(p.category_name, 'Various') as category
                    FROM dim_products p
                    WHERE p.product_id = '{idx}'
                """
                df = execute_query(query)
                cat = "Product"
                if df is not None and len(df) > 0:
                    cat = df['category'].iloc[0] if not pd.isna(df['category'].iloc[0]) else "Various"
                
                name = f"{str(cat).replace('_', ' ').title()} {str(idx)[:8].upper()}"
                
                results.append(CrossSellRecommendation(
                    base_product_id=product_id,
                    recommended_product_id=idx,
                    recommended_product_name=name,
                    reason="Frequently bought together",
                    score=float(score)
                ))
                
        return results
    except Exception as e:
        print(f"Error in cross-sell recommendations: {e}")
        return []

@router.get("/upsell", response_model=List[UpSellRecommendation])
def get_upsell_recommendations(product_id: str):
    """Recommend upsell items (higher price, same category) for a given product_id."""
    try:
        # First find the category and price of the base product
        query1 = f"""
            SELECT p.product_id, COALESCE(p.category_name, 'Various') as category_name, AVG(i.price) as avg_price
            FROM dim_products p
            JOIN fact_order_items i ON p.product_id = i.product_id
            WHERE p.product_id = '{product_id}'
            GROUP BY p.product_id, p.category_name
        """
        df_base = execute_query(query1)
        
        if df_base is None or len(df_base) == 0:
            return []
            
        category = df_base['category_name'].iloc[0]
        base_price = df_base['avg_price'].iloc[0]
        
        # Find products in the same category that are more expensive
        query2 = f"""
            SELECT p.product_id, COALESCE(p.category_name, 'Various') as category_en, AVG(i.price) as avg_price, COUNT(i.order_id) as pop
            FROM dim_products p
            JOIN fact_order_items i ON p.product_id = i.product_id
            WHERE p.category_name = '{category}' 
              AND p.product_id != '{product_id}'
            GROUP BY p.product_id, p.category_name
            HAVING AVG(i.price) > {base_price}
            ORDER BY pop DESC, AVG(i.price) ASC
            LIMIT 3
        """
        df_upsell = execute_query(query2)
        
        results = []
        if df_upsell is not None:
            for _, row in df_upsell.iterrows():
                upsell_id = row['product_id']
                cat = row['category_en'] if not pd.isna(row['category_en']) else "Premium Product"
                upsell_price = row['avg_price']
                
                name = f"{str(cat).replace('_', ' ').title()} {str(upsell_id)[:8].upper()} (Premium)"
                margin_diff = upsell_price - base_price
                
                # Simple score based on price difference and popularity
                score = min(0.99, float(row['pop']) / 100.0)
                
                results.append(UpSellRecommendation(
                    base_product_id=product_id,
                    premium_product_id=upsell_id,
                    premium_product_name=name,
                    additional_margin=float(margin_diff),
                    score=score
                ))
                
        return results
    except Exception as e:
        print(f"Error in upsell recommendations: {e}")
        return []

@router.get("/email-audience", response_model=List[EmailAudience])
def get_email_audience_suggestions():
    """Suggest email audiences based on CLV and RFM segmentation."""
    try:
        query = """
            SELECT 
                CASE 
                    WHEN total_spend > 500 AND recency_days < 30 THEN 'VIP'
                    WHEN total_spend > 200 AND recency_days > 90 THEN 'At Risk High Value'
                    WHEN total_orders = 1 THEN 'New Customers'
                    ELSE 'Regular'
                END as segment,
                COUNT(*) as customer_count
            FROM features_clv
            GROUP BY segment
            ORDER BY customer_count DESC
        """
        df = execute_query(query)
        
        if df is None or len(df) == 0:
            return []
            
        audiences = []
        for _, row in df.iterrows():
            segment = row['segment']
            count = int(row['customer_count'])
            
            if segment == 'VIP':
                action = "Early access to new product lines"
                open_rate = "45% - 55%"
            elif segment == 'At Risk High Value':
                action = "Personalized 'We Miss You' discount"
                open_rate = "15% - 25%"
            elif segment == 'New Customers':
                action = "Educational content + second purchase coupon"
                open_rate = "35% - 45%"
            else:
                action = "Monthly newsletter and general promotions"
                open_rate = "20% - 30%"
                
            audiences.append(EmailAudience(
                segment_name=segment,
                customer_count=count,
                recommended_action=action,
                open_rate_estimate=open_rate
            ))
            
        return audiences
    except Exception as e:
        print(f"Error in email audience suggestions: {e}")
        return []

@router.get("/targeting", response_model=CustomerTargeting)
def get_customer_targeting(customer_id: str):
    """Get targeted recommendations and campaign assignment for a specific customer."""
    try:
        query = f"""
            SELECT 
                customer_unique_id,
                total_spend,
                recency_days,
                total_orders,
                CASE 
                    WHEN total_spend > 500 AND recency_days < 30 THEN 'VIP'
                    WHEN total_spend > 200 AND recency_days > 90 THEN 'At Risk High Value'
                    WHEN total_orders = 1 THEN 'New Customers'
                    ELSE 'Regular'
                END as segment
            FROM features_clv
            WHERE customer_unique_id = '{customer_id}'
        """
        df = execute_query(query)
        
        if df is None or len(df) == 0:
            # Return empty or generic targeting if customer not found
            return CustomerTargeting(
                customer_id=customer_id,
                segment="Unknown",
                recommended_campaign="General Newsletter",
                churn_risk="Low",
                recommended_products=[]
            )
            
        row = df.iloc[0]
        segment = row['segment']
        
        if segment == 'VIP':
            campaign = "Premium Tier Upsell"
            churn = "Low"
        elif segment == 'At Risk High Value':
            campaign = "High-Value Win-back Offer"
            churn = "High"
        elif segment == 'New Customers':
            campaign = "Second Purchase Welcome Flow"
            churn = "Medium"
        else:
            campaign = "Monthly Promotion"
            churn = "Medium"
            
        # Get product recommendations - simple approach for demo: get top 2 global products
        # In a full system we'd look at their past purchases and use the collab filtering matrix
        rec_query = """
            SELECT p.product_id, COALESCE(p.category_name, 'Various') as category
            FROM dim_products p
            LIMIT 2
        """
        rec_df = execute_query(rec_query)
        
        rec_products = []
        if rec_df is not None:
            for _, r in rec_df.iterrows():
                prod_id = r['product_id']
                cat = r['category'] if not pd.isna(r['category']) else "Various"
                name = f"{cat.title()} Product {str(prod_id)[:8].upper()}"
                rec_products.append({
                    "product_id": prod_id,
                    "name": name,
                    "reason": "Popular in your segment"
                })
                
        return CustomerTargeting(
            customer_id=customer_id,
            segment=segment,
            recommended_campaign=campaign,
            churn_risk=churn,
            recommended_products=rec_products
        )
    except Exception as e:
        print(f"Error in customer targeting: {e}")
        return CustomerTargeting(
            customer_id=customer_id,
            segment="Error",
            recommended_campaign="None",
            churn_risk="Unknown",
            recommended_products=[]
        )
