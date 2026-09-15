import os
import json
from dotenv import load_dotenv
from backend.database import execute_query

load_dotenv()

DATABASE_SCHEMA = """
Tables available:
1. agg_monthly_revenue
   Columns: revenue_month (TIMESTAMP), total_revenue (DOUBLE), total_freight (DOUBLE), total_orders (BIGINT), total_customers (BIGINT)
2. agg_category_performance
   Columns: category_name (VARCHAR), total_revenue (DOUBLE), units_sold (BIGINT)
3. dim_customers
   Columns: customer_id (VARCHAR), customer_unique_id (VARCHAR), zip_code (BIGINT), city (VARCHAR), state (VARCHAR)
4. fact_order_items
   Columns: order_id (VARCHAR), customer_id (VARCHAR), product_id (VARCHAR), seller_id (VARCHAR), order_status (VARCHAR), purchase_timestamp (TIMESTAMP), delivered_timestamp (TIMESTAMP), price (DOUBLE), freight_value (DOUBLE), total_item_value (DOUBLE)
"""

def fallback_sql_generator(question: str) -> str:
    """Heuristic fallback SQL generator when LLM API key is not configured."""
    q = question.lower()
    if "category" in q or "categories" in q or "product" in q:
        return "SELECT category_name, total_revenue, units_sold FROM agg_category_performance ORDER BY total_revenue DESC LIMIT 10"
    elif "month" in q or "trend" in q or "timeline" in q or "growth" in q:
        return "SELECT strftime(revenue_month, '%Y-%m') as month, total_revenue, total_orders FROM agg_monthly_revenue ORDER BY revenue_month"
    elif "customer" in q or "city" in q or "state" in q:
        return "SELECT state, count(*) as total_customers FROM dim_customers GROUP BY state ORDER BY total_customers DESC LIMIT 10"
    elif "order" in q or "status" in q:
        return "SELECT order_status, count(*) as count, sum(total_item_value) as total_value FROM fact_order_items GROUP BY order_status"
    else:
        return "SELECT SUM(total_revenue) as total_revenue, SUM(total_orders) as total_orders, SUM(total_customers) as total_customers FROM agg_monthly_revenue"

def generate_sql(user_question: str) -> str:
    """Translates a natural language question into SQL using Groq or heuristic fallback."""
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key and api_key.startswith("gsk_"):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            prompt = f"""
You are an expert Data Analyst using DuckDB.
Translate the following user question into a standard SQL query using the provided schema.
Always return ONLY the SQL query, without markdown formatting or explanation.

Schema:
{DATABASE_SCHEMA}

Question: {user_question}
"""
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0,
                max_tokens=500
            )
            sql = response.choices[0].message.content.strip()
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]
            return sql.strip()
        except Exception as e:
            print(f"Groq API SQL generation failed, using heuristic: {e}")

    return fallback_sql_generator(user_question)

def analyze_results(user_question: str, query: str, data_json: str, data_records: list) -> dict:
    """Analyzes SQL results and generates a business summary."""
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key and api_key.startswith("gsk_"):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            prompt = f"""
You are an AI Business Intelligence Analyst.
Analyze the following data returned from a SQL query to answer the user's question.

User Question: {user_question}
SQL Query executed: {query}
Data Results (JSON): {data_json}

Provide a JSON response with the following keys:
- "summary": A brief executive summary (2-3 sentences) answering the question based on the data.
- "insights": An array of 2-3 key findings (bullet points).
- "recommended_chart": A string ("bar", "line", "pie", or "number") suggesting how to visualize this.
"""
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Groq API analysis failed, using local analysis: {e}")

    # Local fallback analytical summary
    rec_chart = "table"
    if data_records and len(data_records) > 0:
        first_row = data_records[0]
        keys = list(first_row.keys())
        if any("month" in k or "date" in k for k in keys):
            rec_chart = "line"
        elif any("category" in k or "state" in k or "status" in k for k in keys):
            rec_chart = "bar"
        elif len(keys) <= 3 and len(data_records) == 1:
            rec_chart = "number"

    return {
        "summary": f"Query executed successfully returning {len(data_records)} record(s) answering: '{user_question}'.",
        "insights": [
            f"Executed analytical query: `{query}`",
            f"Retrieved {len(data_records)} data points for review."
        ],
        "recommended_chart": rec_chart
    }

def ask_question(question: str) -> dict:
    """End-to-end pipeline: NLQ -> SQL -> Execute -> Analyze."""
    sql_query = generate_sql(question)
    if not sql_query:
        sql_query = fallback_sql_generator(question)
        
    try:
        df = execute_query(sql_query)
        if df is None or len(df) == 0:
            return {
                "question": question,
                "sql": sql_query,
                "data": [],
                "analysis": {
                    "summary": "The query executed successfully but returned 0 results.",
                    "insights": ["Try broadening your filter criteria."],
                    "recommended_chart": "table"
                }
            }
            
        limited_df = df.head(50)
        data_json = limited_df.to_json(orient="records")
        data_records = limited_df.to_dict(orient="records")
        
    except Exception as e:
        return {
            "question": question,
            "sql": sql_query,
            "data": [],
            "error": f"Failed to execute query: {str(e)}",
            "analysis": {
                "summary": "Could not execute the generated SQL query.",
                "insights": [str(e)],
                "recommended_chart": "table"
            }
        }
        
    analysis = analyze_results(question, sql_query, data_json, data_records)
    
    return {
        "question": question,
        "sql": sql_query,
        "data": data_records,
        "analysis": analysis
    }
