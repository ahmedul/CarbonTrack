"""
DynamoDB operations for CSRD Compliance Module
Handles all database CRUD operations for CSRD reports, audit trails, and metrics history
"""

import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
import uuid

from app.models.csrd import (
    CSRDReport,
    CSRDReportSummary,
    AuditTrailEntry,
    ComplianceStatus,
    ReportingPeriod,
    CSRDStandard
)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
ENVIRONMENT = 'prod'

# Table references
reports_table = dynamodb.Table(f'carbontrack-csrd-reports-{ENVIRONMENT}')
audit_table = dynamodb.Table(f'carbontrack-csrd-audit-trail-{ENVIRONMENT}')
metrics_table = dynamodb.Table(f'carbontrack-csrd-metrics-history-{ENVIRONMENT}')


class CSRDDatabase:
    """Database operations for CSRD module"""
    
    @staticmethod
    def _convert_decimals(obj):
        """Convert Decimal objects to float for JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: CSRDDatabase._convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [CSRDDatabase._convert_decimals(item) for item in obj]
        return obj
    
    @staticmethod
    def _prepare_for_dynamodb(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data for DynamoDB storage (float to Decimal)"""
        if isinstance(data, dict):
            return {k: CSRDDatabase._prepare_for_dynamodb(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [CSRDDatabase._prepare_for_dynamodb(item) for item in data]
        elif isinstance(data, float):
            return Decimal(str(data))
        return data
    
    @staticmethod
    async def create_report(report: CSRDReport, user_id: str, ip_address: str) -> CSRDReport:
        """Create a new CSRD report"""
        
        # Generate unique ID if not provided
        if not report.report_id:
            report.report_id = str(uuid.uuid4())
        
        # Set timestamps
        now = datetime.utcnow().isoformat()
        report.created_at = now
        report.updated_at = now
        
        # Prepare item for DynamoDB
        item = CSRDDatabase._prepare_for_dynamodb(report.dict())
        
        # Save to DynamoDB
        reports_table.put_item(Item=item)
        
        # Create audit trail entry
        await CSRDDatabase._add_audit_entry(
            report_id=report.report_id,
            action="CREATED",
            user_id=user_id,
            changes={"status": "Report created"},
            ip_address=ip_address
        )
        
        return report
    
    @staticmethod
    async def get_report(report_id: str) -> Optional[CSRDReport]:
        """Get a specific CSRD report by ID"""
        
        response = reports_table.get_item(Key={'report_id': report_id})
        
        if 'Item' not in response:
            return None
        
        # Convert Decimals and create model
        item = CSRDDatabase._convert_decimals(response['Item'])
        return CSRDReport(**item)
    
    @staticmethod
    async def list_reports(
        company_id: str,
        reporting_year: Optional[int] = None,
        status: Optional[ComplianceStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[CSRDReportSummary], int]:
        """List CSRD reports with filtering and pagination"""
        
        # Build query
        if reporting_year:
            # Query by company and year
            response = reports_table.query(
                IndexName='CompanyYearIndex',
                KeyConditionExpression=Key('company_id').eq(company_id) & Key('reporting_year').eq(reporting_year)
            )
        else:
            # Query by company only
            response = reports_table.query(
                IndexName='CompanyCreatedIndex',
                KeyConditionExpression=Key('company_id').eq(company_id),
                ScanIndexForward=False  # Most recent first
            )
        
        items = response.get('Items', [])
        
        # Filter by status if provided
        if status:
            items = [item for item in items if item.get('status') == status.value]
        
        # Convert to summaries
        summaries = []
        for item in items:
            item = CSRDDatabase._convert_decimals(item)
            summary = CSRDReportSummary(
                report_id=item['report_id'],
                company_name=item['company_name'],
                reporting_year=item['reporting_year'],
                reporting_period=ReportingPeriod(item['reporting_period']),
                status=ComplianceStatus(item['status']),
                completeness_score=item.get('completeness_score', 0),
                created_at=item['created_at'],
                updated_at=item['updated_at'],
                submitted_at=item.get('submitted_at')
            )
            summaries.append(summary)
        
        # Apply pagination
        total = len(summaries)
        summaries = summaries[skip:skip + limit]
        
        return summaries, total
    
    @staticmethod
    async def update_report(
        report_id: str,
        updates: Dict[str, Any],
        user_id: str,
        ip_address: str
    ) -> Optional[CSRDReport]:
        """Update a CSRD report"""
        
        # Get existing report
        report = await CSRDDatabase.get_report(report_id)
        if not report:
            return None
        
        # Track changes for audit
        changes = {}
        for key, new_value in updates.items():
            old_value = getattr(report, key, None)
            if old_value != new_value:
                changes[key] = {"old": old_value, "new": new_value}
        
        # Update timestamp
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        # Build update expression
        update_expr_parts = []
        expr_attr_names = {}
        expr_attr_values = {}
        
        for i, (key, value) in enumerate(updates.items()):
            attr_name = f"#attr{i}"
            attr_value = f":val{i}"
            update_expr_parts.append(f"{attr_name} = {attr_value}")
            expr_attr_names[attr_name] = key
            expr_attr_values[attr_value] = CSRDDatabase._prepare_for_dynamodb(value)
        
        update_expression = "SET " + ", ".join(update_expr_parts)
        
        # Update in DynamoDB
        response = reports_table.update_item(
            Key={'report_id': report_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW"
        )
        
        # Create audit trail entry
        await CSRDDatabase._add_audit_entry(
            report_id=report_id,
            action="UPDATED",
            user_id=user_id,
            changes=changes,
            ip_address=ip_address
        )
        
        # Return updated report
        item = CSRDDatabase._convert_decimals(response['Attributes'])
        return CSRDReport(**item)
    
    @staticmethod
    async def submit_report(
        report_id: str,
        user_id: str,
        ip_address: str
    ) -> Optional[CSRDReport]:
        """Submit a CSRD report for review"""
        
        now = datetime.utcnow().isoformat()
        
        updates = {
            'status': ComplianceStatus.SUBMITTED.value,
            'submitted_at': now,
            'submitted_by': user_id
        }
        
        report = await CSRDDatabase.update_report(report_id, updates, user_id, ip_address)
        
        if report:
            await CSRDDatabase._add_audit_entry(
                report_id=report_id,
                action="SUBMITTED",
                user_id=user_id,
                changes={"status": f"Report submitted at {now}"},
                ip_address=ip_address
            )
        
        return report
    
    @staticmethod
    async def verify_report(
        report_id: str,
        verifier_name: str,
        verifier_license: str,
        verification_date: str,
        notes: Optional[str],
        user_id: str,
        ip_address: str
    ) -> Optional[CSRDReport]:
        """Add third-party verification to a report"""
        
        verification_data = {
            'verified': True,
            'verification_date': verification_date,
            'verifier_name': verifier_name,
            'verifier_license': verifier_license,
            'verification_notes': notes or ""
        }
        
        report = await CSRDDatabase.update_report(report_id, verification_data, user_id, ip_address)
        
        if report:
            await CSRDDatabase._add_audit_entry(
                report_id=report_id,
                action="VERIFIED",
                user_id=user_id,
                changes={
                    "verifier": verifier_name,
                    "license": verifier_license,
                    "date": verification_date
                },
                ip_address=ip_address
            )
        
        return report
    
    @staticmethod
    async def delete_report(report_id: str, user_id: str, ip_address: str) -> bool:
        """Delete a CSRD report (soft delete - mark as deleted)"""
        
        updates = {
            'status': 'DELETED',
            'deleted_at': datetime.utcnow().isoformat(),
            'deleted_by': user_id
        }
        
        report = await CSRDDatabase.update_report(report_id, updates, user_id, ip_address)
        
        if report:
            await CSRDDatabase._add_audit_entry(
                report_id=report_id,
                action="DELETED",
                user_id=user_id,
                changes={"status": "Report deleted"},
                ip_address=ip_address
            )
            return True
        
        return False
    
    @staticmethod
    async def get_audit_trail(report_id: str) -> List[AuditTrailEntry]:
        """Get audit trail for a report"""
        
        response = audit_table.query(
            IndexName='ReportTimeIndex',
            KeyConditionExpression=Key('report_id').eq(report_id),
            ScanIndexForward=False  # Most recent first
        )
        
        items = response.get('Items', [])
        
        audit_entries = []
        for item in items:
            item = CSRDDatabase._convert_decimals(item)
            entry = AuditTrailEntry(
                entry_id=item['entry_id'],
                report_id=item['report_id'],
                timestamp=item['timestamp'],
                user_id=item['user_id'],
                action=item['action'],
                changes=item.get('changes', {}),
                ip_address=item.get('ip_address')
            )
            audit_entries.append(entry)
        
        return audit_entries
    
    @staticmethod
    async def _add_audit_entry(
        report_id: str,
        action: str,
        user_id: str,
        changes: Dict[str, Any],
        ip_address: str
    ):
        """Internal method to add audit trail entry"""
        
        entry = {
            'entry_id': str(uuid.uuid4()),
            'report_id': report_id,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'changes': changes,
            'ip_address': ip_address
        }
        
        audit_table.put_item(Item=CSRDDatabase._prepare_for_dynamodb(entry))
    
    @staticmethod
    async def save_metrics_snapshot(
        company_id: str,
        metrics: Dict[str, Any],
        reporting_date: str
    ):
        """Save metrics snapshot for historical trend analysis"""
        
        metric_item = {
            'metric_id': str(uuid.uuid4()),
            'company_id': company_id,
            'date': reporting_date,
            'metrics': metrics,
            'created_at': datetime.utcnow().isoformat()
        }
        
        metrics_table.put_item(Item=CSRDDatabase._prepare_for_dynamodb(metric_item))
    
    @staticmethod
    async def get_metrics_history(
        company_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get historical metrics for trend analysis"""
        
        key_condition = Key('company_id').eq(company_id)
        
        if start_date and end_date:
            key_condition &= Key('date').between(start_date, end_date)
        elif start_date:
            key_condition &= Key('date').gte(start_date)
        
        response = metrics_table.query(
            IndexName='CompanyDateIndex',
            KeyConditionExpression=key_condition,
            ScanIndexForward=True  # Chronological order
        )
        
        items = response.get('Items', [])
        return [CSRDDatabase._convert_decimals(item) for item in items]
    
    @staticmethod
    async def calculate_completeness(report: CSRDReport) -> float:
        """Calculate report completeness percentage"""
        
        total_fields = 0
        filled_fields = 0
        
        # Check company info
        company_fields = ['company_name', 'company_id', 'company_registration', 
                         'fiscal_year_start', 'fiscal_year_end']
        for field in company_fields:
            total_fields += 1
            if getattr(report, field, None):
                filled_fields += 1
        
        # Check emissions scope
        if report.emissions_scope:
            total_fields += 4
            if report.emissions_scope.scope_1: filled_fields += 1
            if report.emissions_scope.scope_2: filled_fields += 1
            if report.emissions_scope.scope_3: filled_fields += 1
            if report.emissions_scope.total: filled_fields += 1
        
        # Check ESRS metrics (20+ fields)
        if report.esrs_metrics:
            metrics_dict = report.esrs_metrics.dict()
            for key, value in metrics_dict.items():
                total_fields += 1
                if value is not None and value != 0:
                    filled_fields += 1
        
        # Check standards coverage
        if report.standards_covered:
            filled_fields += len(report.standards_covered)
        total_fields += len(CSRDStandard)
        
        # Calculate percentage
        if total_fields == 0:
            return 0.0
        
        return round((filled_fields / total_fields) * 100, 2)


# Singleton instance
csrd_db = CSRDDatabase()
