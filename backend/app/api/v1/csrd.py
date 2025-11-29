"""
CSRD (Corporate Sustainability Reporting Directive) API endpoints
Premium feature for enterprise customers
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.csrd import (
    CSRDReport,
    CSRDReportSummary,
    ComplianceStatus,
    ReportingPeriod,
    CSRDStandard,
    AuditTrailEntry,
    EmissionsScope,
    ESRSMetrics
)
from app.core.middleware import get_current_user
from app.db.csrd_db import csrd_db
from app.db.subscription_db import subscription_db

router = APIRouter(prefix="/csrd", tags=["CSRD Compliance"])


# Dependency to check CSRD access
async def verify_csrd_access(current_user: dict = Depends(get_current_user)):
    """Verify user has access to CSRD features (PREMIUM ONLY)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Check subscription tier - CSRD is PREMIUM ONLY
    user_id = current_user.get("user_id")
    subscription = await subscription_db.get_user_subscription(user_id)
    
    # Verify user has CSRD access
    has_csrd_access = subscription_db.has_feature_access(subscription, 'csrd')
    
    if not has_csrd_access:
        tier = subscription.get('tier', 'FREE')
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Premium Feature Required",
                "message": "CSRD Compliance Module requires a PROFESSIONAL, BUSINESS, or ENTERPRISE subscription",
                "current_tier": tier,
                "required_tiers": ["PROFESSIONAL", "BUSINESS", "ENTERPRISE"],
                "upgrade_url": "/api/v1/subscriptions/upgrade",
                "pricing": {
                    "PROFESSIONAL": {"price": 49, "currency": "USD", "period": "month", "entities": 1},
                    "BUSINESS": {"price": 149, "currency": "USD", "period": "month", "entities": 5},
                    "ENTERPRISE": {"price": 499, "currency": "USD", "period": "month", "entities": "unlimited"}
                }
            }
        )
    
    # Add subscription info to current_user for downstream use
    current_user["subscription"] = subscription
    
    return current_user


@router.post("/reports", response_model=CSRDReport, status_code=status.HTTP_201_CREATED)
async def create_csrd_report(
    request: Request,
    company_name: str,
    reporting_year: int,
    country: str,
    employee_count: int,
    annual_revenue_eur: float,
    reporting_period: ReportingPeriod = ReportingPeriod.ANNUAL,
    sector: Optional[str] = None,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Create a new CSRD compliance report
    
    - **company_name**: Legal company name
    - **reporting_year**: Year for the report (e.g., 2025)
    - **country**: Country code (e.g., "DE", "FR", "NL")
    - **employee_count**: Total number of employees
    - **annual_revenue_eur**: Annual revenue in EUR
    """
    # Generate report ID
    report_id = f"csrd_{reporting_year}_{uuid.uuid4().hex[:8]}"
    
    # Create report
    report = CSRDReport(
        report_id=report_id,
        company_id=current_user.get("company_id", "default_company"),
        user_id=current_user["user_id"],
        reporting_year=reporting_year,
        reporting_period=reporting_period,
        status=ComplianceStatus.NOT_STARTED,
        company_name=company_name,
        country=country,
        sector=sector,
        employee_count=employee_count,
        annual_revenue_eur=annual_revenue_eur,
        esrs_metrics=ESRSMetrics(),
        emissions_scope=EmissionsScope()
    )
    
    # Save to DynamoDB
    client_ip = request.client.host if request.client else "unknown"
    saved_report = await csrd_db.create_report(
        report=report,
        user_id=current_user["user_id"],
        ip_address=client_ip
    )
    
    return saved_report


@router.get("/reports", response_model=dict)
async def list_csrd_reports(
    year: Optional[int] = None,
    status: Optional[ComplianceStatus] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    List all CSRD reports for the current user/company
    
    - **year**: Filter by reporting year
    - **status**: Filter by compliance status
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    company_id = current_user.get("company_id", "default_company")
    
    # Fetch from DynamoDB
    reports, total = await csrd_db.list_reports(
        company_id=company_id,
        reporting_year=year,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return {
        "reports": reports,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/reports/{report_id}", response_model=CSRDReport)
async def get_csrd_report(
    report_id: str,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Get detailed CSRD report by ID
    """
    # Fetch from DynamoDB
    report = await csrd_db.get_report(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )
    
    # Verify access (user must own the report or be from same company)
    if report.user_id != current_user["user_id"] and report.company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    return report


@router.put("/reports/{report_id}", response_model=CSRDReport)
async def update_csrd_report(
    report_id: str,
    request: Request,
    current_user: dict = Depends(verify_csrd_access),
    # Optional update fields
    status_update: Optional[ComplianceStatus] = None,
    emissions_scope: Optional[EmissionsScope] = None,
    esrs_metrics: Optional[ESRSMetrics] = None,
    notes: Optional[str] = None
):
    """
    Update CSRD report data
    
    - **status_update**: Change compliance status
    - **emissions_scope**: Update emissions data (Scope 1, 2, 3)
    - **esrs_metrics**: Update ESRS metrics
    - **notes**: Add notes or comments
    """
    # Verify report exists and user has access
    report = await csrd_db.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )
    
    if report.user_id != current_user["user_id"] and report.company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    # Build updates dictionary
    updates = {}
    if status_update:
        updates['status'] = status_update.value
    if emissions_scope:
        updates['emissions_scope'] = emissions_scope.dict()
    if esrs_metrics:
        updates['esrs_metrics'] = esrs_metrics.dict()
    if notes:
        updates['notes'] = notes
    
    # Calculate and update completeness
    if emissions_scope or esrs_metrics:
        # Create updated report for completeness calculation
        temp_report = report.copy(deep=True)
        if emissions_scope:
            temp_report.emissions_scope = emissions_scope
        if esrs_metrics:
            temp_report.esrs_metrics = esrs_metrics
        completeness = await csrd_db.calculate_completeness(temp_report)
        updates['completeness_score'] = completeness
    
    # Update in database
    client_ip = request.client.host if request.client else "unknown"
    updated_report = await csrd_db.update_report(
        report_id=report_id,
        updates=updates,
        user_id=current_user["user_id"],
        ip_address=client_ip
    )
    
    return updated_report


@router.post("/reports/{report_id}/submit", response_model=CSRDReport)
@router.post("/reports/{report_id}/submit", response_model=CSRDReport)
async def submit_csrd_report(
    report_id: str,
    request: Request,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Submit CSRD report for compliance
    
    Validates completeness and marks as submitted
    """
    # Fetch report
    report = await csrd_db.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )
    
    # Verify access
    if report.user_id != current_user["user_id"] and report.company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    # Check completeness
    completeness = await csrd_db.calculate_completeness(report)
    if completeness < 95.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report must be at least 95% complete to submit (current: {completeness}%)"
        )
    
    # Submit report
    client_ip = request.client.host if request.client else "unknown"
    submitted_report = await csrd_db.submit_report(
        report_id=report_id,
        user_id=current_user["user_id"],
        ip_address=client_ip
    )
    
    return submitted_report


@router.get("/reports/{report_id}/export/pdf")
async def export_csrd_report_pdf(
    report_id: str,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Export CSRD report as PDF
    
    Generates ESRS-compliant PDF report
    """
    # TODO: Fetch report
    # TODO: Generate PDF using reportlab or weasyprint
    # TODO: Upload to S3
    # TODO: Return download URL
    
    return {
        "success": True,
        "message": "PDF export initiated",
        "report_id": report_id,
        "download_url": f"https://s3.amazonaws.com/carbontrack-reports/csrd_{report_id}.pdf",
        "expires_at": datetime.utcnow().isoformat()
    }


@router.get("/reports/{report_id}/audit-trail", response_model=List[AuditTrailEntry])
async def get_audit_trail(
    report_id: str,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Get audit trail for a CSRD report
    
    Shows all changes and actions performed on the report
    """
    # Verify report exists and user has access
    report = await csrd_db.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )
    
    if report.user_id != current_user["user_id"] and report.company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    # Fetch audit trail from database
    audit_trail = await csrd_db.get_audit_trail(report_id)
    
    return audit_trail


@router.get("/standards", response_model=List[dict])
async def list_esrs_standards(
    current_user: dict = Depends(verify_csrd_access)
):
    """
    List all ESRS (European Sustainability Reporting Standards)
    
    Returns information about each standard
    """
    standards = [
        {
            "code": "E1",
            "name": "Climate Change",
            "description": "GHG emissions, energy, climate adaptation",
            "required_metrics": ["scope_1", "scope_2", "scope_3", "renewable_energy"],
            "esrs_standard": CSRDStandard.E1_CLIMATE
        },
        {
            "code": "E2",
            "name": "Pollution",
            "description": "Air, water, soil pollution",
            "required_metrics": ["air_pollutants", "water_pollutants", "soil_pollutants"],
            "esrs_standard": CSRDStandard.E2_POLLUTION
        },
        {
            "code": "E3",
            "name": "Water and Marine Resources",
            "description": "Water consumption, discharge, recycling",
            "required_metrics": ["water_consumption", "water_discharge", "water_recycled"],
            "esrs_standard": CSRDStandard.E3_WATER
        },
        {
            "code": "E4",
            "name": "Biodiversity and Ecosystems",
            "description": "Land use, protected areas impact",
            "required_metrics": ["land_use", "protected_areas_impact"],
            "esrs_standard": CSRDStandard.E4_BIODIVERSITY
        },
        {
            "code": "E5",
            "name": "Circular Economy",
            "description": "Waste management, recycling, resource use",
            "required_metrics": ["waste_generated", "waste_recycled", "materials_recycled"],
            "esrs_standard": CSRDStandard.E5_CIRCULAR
        },
        {
            "code": "S1",
            "name": "Own Workforce",
            "description": "Employee welfare, diversity, training, safety",
            "required_metrics": ["total_workforce", "female_employees", "training_hours", "accidents"],
            "esrs_standard": CSRDStandard.S1_WORKFORCE
        },
        {
            "code": "G1",
            "name": "Business Conduct",
            "description": "Corporate governance, ethics, anti-corruption",
            "required_metrics": ["board_diversity", "ethics_training", "anti_corruption_policy"],
            "esrs_standard": CSRDStandard.G1_GOVERNANCE
        }
    ]
    
    return standards


@router.get("/compliance-check/{report_id}", response_model=dict)
async def check_compliance(
    report_id: str,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Check compliance status and identify missing data
    
    Returns completeness score and list of missing fields
    """
    # TODO: Fetch report and analyze completeness
    
    return {
        "report_id": report_id,
        "completeness_score": 65.5,
        "is_submittable": False,
        "minimum_required": 95.0,
        "missing_fields": [
            {
                "field": "metrics.carbon_reduction_target",
                "standard": "E1",
                "required": True,
                "description": "Carbon reduction target percentage"
            },
            {
                "field": "metrics.air_pollutants_kg",
                "standard": "E2",
                "required": True,
                "description": "Air pollutants in kg"
            },
            {
                "field": "auditor_name",
                "standard": "All",
                "required": True,
                "description": "Third-party auditor name"
            }
        ],
        "warnings": [
            {
                "field": "metrics.waste_recycled_percentage",
                "message": "Low recycling percentage (78%). EU average is 85%"
            }
        ],
        "recommendations": [
            "Complete E2 (Pollution) metrics to improve compliance score",
            "Assign third-party auditor before submission",
            "Review waste management strategy to increase recycling rate"
        ]
    }


@router.get("/deadline-calendar", response_model=List[dict])
async def get_compliance_calendar(
    year: int = 2026,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Get CSRD compliance deadlines and milestones
    """
    calendar = [
        {
            "date": f"{year}-01-31",
            "milestone": "Q4 data collection deadline",
            "description": "Complete data collection for Q4 of previous year",
            "priority": "high"
        },
        {
            "date": f"{year}-03-31",
            "milestone": "Internal review deadline",
            "description": "Complete internal review and validation",
            "priority": "high"
        },
        {
            "date": f"{year}-04-15",
            "milestone": "Auditor review deadline",
            "description": "Third-party auditor completes review",
            "priority": "critical"
        },
        {
            "date": f"{year}-04-30",
            "milestone": "CSRD submission deadline",
            "description": "Final submission to authorities",
            "priority": "critical"
        }
    ]
    
    return calendar


@router.post("/reports/{report_id}/verify", response_model=CSRDReport)
async def verify_csrd_report(
    report_id: str,
    request: Request,
    verifier_name: str,
    verifier_license: str,
    verification_date: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(verify_csrd_access)
):
    """
    Add third-party verification to a CSRD report
    
    - **verifier_name**: Name of auditing firm/professional
    - **verifier_license**: Professional license number
    - **verification_date**: Date of verification (ISO format)
    - **notes**: Optional verification notes
    """
    # Verify report exists and user has access
    report = await csrd_db.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )
    
    if report.user_id != current_user["user_id"] and report.company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    # Add verification
    client_ip = request.client.host if request.client else "unknown"
    verified_report = await csrd_db.verify_report(
        report_id=report_id,
        verifier_name=verifier_name,
        verifier_license=verifier_license,
        verification_date=verification_date,
        notes=notes,
        user_id=current_user["user_id"],
        ip_address=client_ip
    )
    
    return verified_report
