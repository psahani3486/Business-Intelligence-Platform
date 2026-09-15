from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from backend.reports.generator import generate_pdf_report

router = APIRouter()

class ReportRequest(BaseModel):
    title: str = "Executive Business Intelligence Report"
    date_range: str = "Last 30 Days"
    include_charts: bool = True

@router.post("/generate")
def generate_report(req: ReportRequest):
    """Generate a PDF report."""
    report_id, filepath = generate_pdf_report(req.title, req.date_range, req.include_charts)
    return {"status": "success", "report_id": report_id, "download_url": f"/api/reports/download/{report_id}"}

@router.get("/download/{report_id}")
def download_report(report_id: str):
    """Download a generated PDF report."""
    reports_dir = os.path.join(os.path.dirname(__file__), '../../reports/output')
    filepath = os.path.join(reports_dir, f"{report_id}.pdf")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
        
    return FileResponse(
        filepath, 
        media_type='application/pdf', 
        filename=f"{report_id}.pdf"
    )
