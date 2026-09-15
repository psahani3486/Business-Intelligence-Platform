# Pulse BI - E-Commerce Analytics & Machine Learning Platform

A full-stack **Business Intelligence Platform** built with **FastAPI**, **DuckDB**, **Next.js**, and **XGBoost**. Designed to analyze large-scale e-commerce datasets (Olist) with predictive revenue forecasting, RFM customer segmentation, anomaly detection, and automated executive PDF reporting.

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Setup & Start Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn backend.api.main:app --reload --port 8000
```
API runs at: **`http://localhost:8000`** (Swagger docs at `http://localhost:8000/docs`)

### 3. Setup & Start Frontend
```bash
# Move to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```
Dashboard runs at: **`http://localhost:3000`**

---

## 🐳 Docker Setup

Run backend and frontend together using Docker Compose:

```bash
docker-compose up --build
```

- **Web Dashboard**: `http://localhost:3000`
- **FastAPI Documentation**: `http://localhost:8000/docs`

---

## 📁 Project Architecture

```text
Business-Intelligence-Platform/
├── backend/                  # FastAPI analytical backend
│   ├── api/
│   │   ├── routes/           # REST endpoints (dashboard, sales, customers, etc.)
│   │   ├── main.py           # FastAPI application entrypoint
│   │   └── schemas.py        # Pydantic data validation schemas
│   ├── database.py           # Embedded DuckDB analytical query engine
│   ├── etl/                  # ETL feature engineering & data loading
│   ├── ml/                   # Machine learning models (XGBoost, Isolation Forest)
│   └── reports/              # PDF executive report generation with ReportLab
├── frontend/                 # Next.js App Router (TypeScript & React 19)
│   ├── src/
│   │   ├── app/              # Dashboard pages (Sales, Customers, Products, etc.)
│   │   ├── components/       # Recharts visualizations & layout components
│   │   └── lib/              # Axios API client & utility functions
├── data/                     # Raw datasets & local DuckDB analytical database
├── tests/                    # API integration and unit test suite
├── docker-compose.yml        # Production Docker Compose orchestration
├── Dockerfile.backend        # Backend container definition
└── requirements.txt          # Python dependencies
```

---

## 🚀 Core Modules

- **📊 Dashboard Overview (`/`)**: High-level executive KPIs, revenue run rates, and operational highlights.
- **📈 Sales & Performance (`/sales`)**: Time-series revenue forecasting, payment breakdowns, and regional market distribution.
- **👥 Customer Insights (`/customers`)**: RFM segmentation, Customer Lifetime Value (CLV), and churn risk action lists.
- **📄 Reports & Export (`/reports`)**: One-click multi-page executive PDF report generation.

---

## 📄 License

Distributed under the MIT License.
