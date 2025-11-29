"""
CSRD (Corporate Sustainability Reporting Directive) models
"""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ReportingPeriod(str, Enum):
    """CSRD reporting period"""
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"
    ANNUAL = "annual"


class CSRDStandard(str, Enum):
    """ESRS standards"""
    E1_CLIMATE = "E1_climate_change"
    E2_POLLUTION = "E2_pollution"
    E3_WATER = "E3_water_marine"
    E4_BIODIVERSITY = "E4_biodiversity"
    E5_CIRCULAR = "E5_circular_economy"
    S1_WORKFORCE = "S1_own_workforce"
    S2_VALUE_CHAIN = "S2_value_chain_workers"
    S3_COMMUNITIES = "S3_affected_communities"
    S4_CONSUMERS = "S4_consumers_end_users"
    G1_GOVERNANCE = "G1_business_conduct"


class ComplianceStatus(str, Enum):
    """Compliance status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    SUBMITTED = "submitted"


class EmissionsScope(BaseModel):
    """Emissions data by scope"""
    scope_1: float = Field(0.0, description="Direct emissions (tCO2e)")
    scope_2: float = Field(0.0, description="Indirect energy emissions (tCO2e)")
    scope_3: float = Field(0.0, description="Value chain emissions (tCO2e)")
    total: float = Field(0.0, description="Total emissions (tCO2e)")
    
    def calculate_total(self):
        """Calculate total emissions"""
        self.total = self.scope_1 + self.scope_2 + self.scope_3
        return self.total


class ESRSMetrics(BaseModel):
    """ESRS (European Sustainability Reporting Standards) metrics"""
    
    # E1: Climate Change
    emissions: EmissionsScope = Field(default_factory=EmissionsScope)
    renewable_energy_percentage: float = Field(0.0, ge=0, le=100)
    energy_consumption_mwh: float = Field(0.0, ge=0)
    carbon_reduction_target: Optional[float] = Field(None, description="Target reduction %")
    
    # E2: Pollution
    air_pollutants_kg: float = Field(0.0, ge=0)
    water_pollutants_kg: float = Field(0.0, ge=0)
    soil_pollutants_kg: float = Field(0.0, ge=0)
    
    # E3: Water
    water_consumption_m3: float = Field(0.0, ge=0)
    water_discharge_m3: float = Field(0.0, ge=0)
    water_recycled_percentage: float = Field(0.0, ge=0, le=100)
    
    # E4: Biodiversity
    land_use_hectares: float = Field(0.0, ge=0)
    protected_areas_impact: Optional[str] = None
    
    # E5: Circular Economy
    waste_generated_tonnes: float = Field(0.0, ge=0)
    waste_recycled_percentage: float = Field(0.0, ge=0, le=100)
    materials_recycled_tonnes: float = Field(0.0, ge=0)
    
    # Social metrics (S1-S4)
    total_workforce: int = Field(0, ge=0)
    female_employees_percentage: float = Field(0.0, ge=0, le=100)
    employee_training_hours: float = Field(0.0, ge=0)
    workplace_accidents: int = Field(0, ge=0)
    
    # Governance (G1)
    board_diversity_percentage: float = Field(0.0, ge=0, le=100)
    ethics_training_completed: bool = Field(False)
    anti_corruption_policy: bool = Field(False)


class CSRDReport(BaseModel):
    """CSRD compliance report"""
    report_id: str = Field(..., description="Unique report ID")
    company_id: str = Field(..., description="Company ID")
    user_id: str = Field(..., description="User who created report")
    
    # Report details
    reporting_year: int = Field(..., description="Year of reporting")
    reporting_period: ReportingPeriod = Field(ReportingPeriod.ANNUAL)
    status: ComplianceStatus = Field(ComplianceStatus.NOT_STARTED)
    
    # Company information
    company_name: str = Field(..., description="Legal company name")
    company_registration_number: Optional[str] = None
    country: str = Field(..., description="Country of incorporation")
    sector: Optional[str] = Field(None, description="Industry sector")
    employee_count: int = Field(0, ge=0)
    annual_revenue_eur: float = Field(0.0, ge=0)
    
    # ESRS metrics
    metrics: ESRSMetrics = Field(default_factory=ESRSMetrics)
    
    # Standards covered
    standards_included: List[CSRDStandard] = Field(default_factory=list)
    
    # Audit information
    auditor_name: Optional[str] = None
    audit_date: Optional[datetime] = None
    auditor_opinion: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    submission_deadline: Optional[datetime] = None
    
    # Data quality
    completeness_score: float = Field(0.0, ge=0, le=100, description="% of required fields filled")
    verified: bool = Field(False, description="Third-party verified")
    
    # Additional notes
    notes: Optional[str] = None
    attachments: List[str] = Field(default_factory=list, description="URLs to supporting documents")
    
    class Config:
        schema_extra = {
            "example": {
                "report_id": "csrd_2025_123",
                "company_id": "company_abc",
                "user_id": "user_123",
                "reporting_year": 2025,
                "reporting_period": "annual",
                "status": "in_progress",
                "company_name": "Green Tech Solutions EU",
                "country": "DE",
                "sector": "Technology",
                "employee_count": 350,
                "annual_revenue_eur": 45000000,
                "metrics": {
                    "emissions": {
                        "scope_1": 450.5,
                        "scope_2": 1200.3,
                        "scope_3": 3500.8,
                        "total": 5151.6
                    },
                    "renewable_energy_percentage": 65.0,
                    "water_consumption_m3": 15000
                },
                "completeness_score": 75.5,
                "submission_deadline": "2026-04-30T00:00:00Z"
            }
        }


class CSRDReportSummary(BaseModel):
    """Summary view of CSRD report"""
    report_id: str
    company_name: str
    reporting_year: int
    status: ComplianceStatus
    completeness_score: float
    total_emissions: float
    submission_deadline: Optional[datetime]
    last_updated: datetime


class AuditTrailEntry(BaseModel):
    """Audit trail for data changes"""
    entry_id: str
    report_id: str
    user_id: str
    action: str  # "created", "updated", "submitted", "verified"
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
