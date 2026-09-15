import logging
from fpdf import FPDF
from datetime import datetime
import os
import uuid
from backend.database import execute_query
from backend.reports.charts import generate_revenue_trend_chart, generate_forecast_chart

logger = logging.getLogger(__name__)

os.makedirs(os.path.join(os.path.dirname(__file__), "output"), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "temp"), exist_ok=True)

class ReportPDF(FPDF):
    def header(self):
        # Company Branding Background
        self.set_fill_color(30, 58, 138) # Tailwind blue-900
        self.rect(0, 0, 210, 25, 'F')
        
        # Logo placeholder (Text)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 8)
        self.cell(50, 10, 'QuantumBI', 0, 0, 'L')
        
        # Title
        self.set_font('Arial', '', 14)
        self.set_text_color(200, 200, 200)
        self.cell(140, 10, 'Enterprise AI Analytics Report', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated automatically by QuantumBI', 0, 0, 'C')
        
    def section_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 58, 138)
        self.cell(0, 10, title, 0, 1, 'L')
        # Separator line
        self.set_draw_color(30, 58, 138)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

def generate_pdf_report(title: str, date_range: str, include_charts: bool = False) -> str:
    """Generates an executive summary PDF and returns the file path."""
    pdf = ReportPDF()
    pdf.add_page()
    
    # Title and Metadata
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, title, 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.cell(0, 6, f"Reporting Period: {date_range}", 0, 1)
    pdf.ln(8)
    
    # --- Executive Summary ---
    pdf.section_title("Executive Summary")
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(50, 50, 50)
    summary_text = (
        "This report provides a high-level overview of key business metrics, including historical "
        "revenue performance and future AI-driven forecasts. The data indicates stable long-term "
        "growth with specific opportunities identified in our anomaly and churn models."
    )
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(8)
    
    # --- KPIs ---
    pdf.section_title("Key Performance Indicators (Lifetime)")
    
    query = """
        SELECT 
            SUM(total_revenue) as rev,
            SUM(total_orders) as ords,
            AVG(total_revenue / NULLIF(total_orders, 0)) as aov
        FROM agg_monthly_revenue
    """
    df = execute_query(query)
    
    if df is not None and len(df) > 0:
        rev = df['rev'].iloc[0] or 0
        ords = df['ords'].iloc[0] or 0
        aov = df['aov'].iloc[0] or 0
    else:
        rev = ords = aov = 0
        
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    
    # 3 columns for KPIs
    col_width = 60
    pdf.cell(col_width, 8, "Total Revenue", border=0, align='C')
    pdf.cell(col_width, 8, "Total Orders", border=0, align='C')
    pdf.cell(col_width, 8, "Avg Order Value", border=0, align='C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(16, 185, 129) # Tailwind green
    pdf.cell(col_width, 10, f"${rev:,.0f}", border=0, align='C')
    pdf.set_text_color(59, 130, 246) # Tailwind blue
    pdf.cell(col_width, 10, f"{int(ords):,}", border=0, align='C')
    pdf.set_text_color(245, 158, 11) # Tailwind amber
    pdf.cell(col_width, 10, f"${aov:,.2f}", border=0, align='C')
    pdf.ln(15)
    
    # --- Charts ---
    if include_charts:
        pdf.section_title("Visual Analytics")
        
        # Trend chart
        trend_img = generate_revenue_trend_chart()
        if trend_img and os.path.exists(trend_img):
            # Place image in center
            pdf.image(trend_img, x=25, w=160)
            os.remove(trend_img) # Cleanup
            pdf.ln(5)
            
        # Forecast chart
        forecast_img = generate_forecast_chart()
        if forecast_img and os.path.exists(forecast_img):
            # Might need a new page if it doesn't fit
            if pdf.get_y() > 200:
                pdf.add_page()
                pdf.section_title("Forecasting")
            pdf.image(forecast_img, x=25, w=160)
            os.remove(forecast_img) # Cleanup
            pdf.ln(10)
            
    # --- Data Table (Top Categories) ---
    pdf.section_title("Top Performing Categories")
    cat_query = """
        SELECT 
            c.product_category_name_english as category,
            COUNT(i.order_item_id) as items_sold,
            SUM(i.price) as revenue
        FROM fact_order_items i
        JOIN dim_products p ON i.product_id = p.product_id
        LEFT JOIN product_category_name_translation c ON p.category_name = c.product_category_name
        WHERE c.product_category_name_english IS NOT NULL
        GROUP BY 1
        ORDER BY revenue DESC
        LIMIT 5
    """
    cat_df = execute_query(cat_query)
    
    if cat_df is not None and len(cat_df) > 0:
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(80, 8, "Category", border=1, fill=True)
        pdf.cell(50, 8, "Items Sold", border=1, align='C', fill=True)
        pdf.cell(60, 8, "Revenue", border=1, align='R', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        for _, row in cat_df.iterrows():
            pdf.cell(80, 8, str(row['category']).replace('_', ' ').title(), border=1)
            pdf.cell(50, 8, f"{int(row['items_sold']):,}", border=1, align='C')
            pdf.cell(60, 8, f"${float(row['revenue']):,.2f}", border=1, align='R')
            pdf.ln()
            
    # Save the file
    reports_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(reports_dir, exist_ok=True)
    
    report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
    filepath = os.path.join(reports_dir, f"{report_id}.pdf")
    
    pdf.output(filepath)
    
    return report_id, filepath
