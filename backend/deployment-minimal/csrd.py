from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create a router for CSRD endpoints
router = APIRouter(
    prefix="/api/v1/csrd",
    tags=["csrd"],
    responses={404: {"description": "Not found"}},
)

# --- Data Models ---

class CSRDMetric(BaseModel):
    """A single metric within a CSRD standard"""
    id: str
    name: str
    value: Any
    unit: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"  # pending, complete, verified

class CSRDStandard(BaseModel):
    """A CSRD standard (e.g., E1 Climate Change)"""
    code: str  # e.g., "E1"
    name: str  # e.g., "Climate Change"
    metrics: List[CSRDMetric] = []
    status: str = "not_started"  # not_started, in_progress, complete

class CSRDReportBase(BaseModel):
    """Base model for CSRD Report"""
    company_name: str
    reporting_year: int
    description: Optional[str] = None

class CSRDReportCreate(CSRDReportBase):
    """Model for creating a new report"""
    pass

class CSRDReport(CSRDReportBase):
    """Full CSRD Report model"""
    id: str
    created_at: datetime
    updated_at: datetime
    status: str = "draft"  # draft, submitted, published
    standards: List[CSRDStandard] = []
    
    # Summary stats
    completion_percentage: float = 0.0

# --- In-Memory Database (Mock) ---

# Sample standards template
DEFAULT_STANDARDS = [
    CSRDStandard(
        code="E1", 
        name="Climate Change", 
        metrics=[
            CSRDMetric(id="E1-1", name="Scope 1 GHG Emissions", value=0, unit="tCO2e"),
            CSRDMetric(id="E1-2", name="Scope 2 GHG Emissions", value=0, unit="tCO2e"),
            CSRDMetric(id="E1-3", name="Scope 3 GHG Emissions", value=0, unit="tCO2e"),
        ]
    ),
    CSRDStandard(
        code="S1", 
        name="Own Workforce", 
        metrics=[
            CSRDMetric(id="S1-1", name="Total Employees", value=0, unit="count"),
            CSRDMetric(id="S1-2", name="Gender Diversity", value=0, unit="%"),
        ]
    ),
    CSRDStandard(
        code="G1", 
        name="Business Conduct", 
        metrics=[
            CSRDMetric(id="G1-1", name="Anti-corruption training", value=0, unit="% employees"),
        ]
    )
]

# Store reports in memory
csrd_reports: Dict[str, CSRDReport] = {}

def generate_csrd_pdf_file(report: CSRDReport, filename: str):
    """Generate a PDF file for the CSRD report"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, f"CSRD Report: {report.company_name}")
    
    # Metadata
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Reporting Year: {report.reporting_year}")
    c.drawString(50, height - 100, f"Status: {report.status}")
    c.drawString(50, height - 120, f"Completion: {report.completion_percentage:.1f}%")
    
    y_position = height - 160
    
    # Standards
    for standard in report.standards:
        if y_position < 100:
            c.showPage()
            y_position = height - 50
            
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y_position, f"{standard.code} - {standard.name}")
        y_position -= 30
        
        c.setFont("Helvetica", 12)
        for metric in standard.metrics:
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                
            c.drawString(70, y_position, f"{metric.id}: {metric.name}")
            # Handle value display
            value_str = str(metric.value)
            c.drawString(400, y_position, f"{value_str} {metric.unit or ''}")
            y_position -= 20
            
        y_position -= 20
        
    c.save()

# --- Endpoints ---

@router.get("/reports", response_model=List[CSRDReport])
async def list_reports():
    """List all CSRD reports"""
    return list(csrd_reports.values())

@router.post("/reports", response_model=CSRDReport, status_code=status.HTTP_201_CREATED)
async def create_report(report_in: CSRDReportCreate):
    """Create a new CSRD report"""
    report_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Create report with default standards
    new_report = CSRDReport(
        id=report_id,
        **report_in.model_dump(),
        created_at=now,
        updated_at=now,
        standards=DEFAULT_STANDARDS, # Initialize with templates
        completion_percentage=0.0
    )
    
    csrd_reports[report_id] = new_report
    return new_report

@router.get("/reports/{report_id}", response_model=CSRDReport)
async def get_report(report_id: str):
    """Get a specific CSRD report by ID"""
    if report_id not in csrd_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    return csrd_reports[report_id]

@router.put("/reports/{report_id}", response_model=CSRDReport)
async def update_report(report_id: str, report_update: CSRDReportBase):
    """Update report metadata"""
    if report_id not in csrd_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = csrd_reports[report_id]
    
    # Update fields
    report.company_name = report_update.company_name
    report.reporting_year = report_update.reporting_year
    report.description = report_update.description
    report.updated_at = datetime.now()
    
    csrd_reports[report_id] = report
    return report

@router.put("/reports/{report_id}/standards/{standard_code}/metrics/{metric_id}", response_model=CSRDReport)
async def update_metric(
    report_id: str, 
    standard_code: str, 
    metric_id: str, 
    value: Any,
    status: str = "complete"
):
    """Update a specific metric value in a report"""
    if report_id not in csrd_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = csrd_reports[report_id]
    
    # Find standard
    standard = next((s for s in report.standards if s.code == standard_code), None)
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    # Find metric
    metric = next((m for m in standard.metrics if m.id == metric_id), None)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # Update metric
    metric.value = value
    metric.status = status
    report.updated_at = datetime.now()
    
    # Recalculate completion
    total_metrics = sum(len(s.metrics) for s in report.standards)
    completed_metrics = sum(
        1 for s in report.standards for m in s.metrics if m.status == "complete"
    )
    report.completion_percentage = (completed_metrics / total_metrics) * 100 if total_metrics > 0 else 0
    
    csrd_reports[report_id] = report
    return report

@router.post("/reports/{report_id}/generate-pdf")
async def generate_pdf(report_id: str):
    """Generate a PDF version of the report"""
    if report_id not in csrd_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = csrd_reports[report_id]
    
    # Create a temporary file
    filename = f"csrd_report_{report_id}.pdf"
    filepath = os.path.join("/tmp", filename)
    
    try:
        generate_csrd_pdf_file(report, filepath)
        return FileResponse(
            path=filepath, 
            filename=filename, 
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
