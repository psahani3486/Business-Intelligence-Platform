from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import (
    dashboard,
    nlq,
    forecasts,
    churn,
    clv,
    anomalies,
    recommendations,
    reports,
    mlops,
)

app = FastAPI(
    title="Business Intelligence Platform API",
    description="FastAPI backend for analytics, ML forecasts, and business intelligence",
    version="1.0.0",
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Enterprise AI BI Platform API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(nlq.router, prefix="/api/nlq", tags=["Natural Language Query"])
app.include_router(forecasts.router, prefix="/api/forecasts", tags=["Forecasts"])
app.include_router(churn.router, prefix="/api/churn", tags=["Churn"])
app.include_router(clv.router, prefix="/api/clv", tags=["CLV"])
app.include_router(anomalies.router, prefix="/api/anomalies", tags=["Anomalies"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(mlops.router, prefix="/api/mlops", tags=["MLOps"])
