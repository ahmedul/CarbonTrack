"""
PDF Import Proof of Concept
Simple implementation of document processing for CarbonTrack
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import tempfile
import os
import re
from datetime import datetime
import json

# Mock implementation - in production would use proper OCR and ML
class MockPDFProcessor:
    """Mock PDF processor for demonstration purposes"""
    
    def __init__(self):
        # Mock document patterns for demonstration
        self.mock_documents = {
            'electricity_bill_sample.pdf': {
                'type': 'electricity_bill',
                'extracted_data': {
                    'kwh_usage': 450.5,
                    'billing_period': '2025-08-01 to 2025-08-31',
                    'total_cost': 89.45,
                    'utility_company': 'Pacific Gas & Electric'
                },
                'calculated_co2_kg': 180.2  # 450.5 * 0.4 kg CO2/kWh
            },
            'gas_bill_sample.pdf': {
                'type': 'gas_bill',
                'extracted_data': {
                    'therm_usage': 25.3,
                    'billing_period': '2025-08-01 to 2025-08-31',
                    'total_cost': 34.21,
                    'utility_company': 'SoCalGas'
                },
                'calculated_co2_kg': 134.09  # 25.3 * 5.3 kg CO2/therm
            },
            'fuel_receipt_sample.pdf': {
                'type': 'fuel_receipt',
                'extracted_data': {
                    'gallons': 12.456,
                    'fuel_type': 'regular',
                    'total_cost': 45.67,
                    'station': 'Shell Gas Station',
                    'date': '2025-09-15'
                },
                'calculated_co2_kg': 110.74  # 12.456 * 8.89 kg CO2/gallon
            },
            'travel_invoice_sample.pdf': {
                'type': 'travel_invoice',
                'extracted_data': {
                    'flight_distance': 2500,  # miles
                    'transport_mode': 'commercial_flight',
                    'trip_type': 'round_trip',
                    'airline': 'United Airlines',
                    'departure_date': '2025-09-20'
                },
                'calculated_co2_kg': 500.0  # 2500 miles * 0.2 kg CO2/mile
            }
        }
    
    def process_document(self, filename: str, file_content: bytes) -> Dict[str, Any]:
        """Mock document processing"""
        
        # Simulate processing time
        import time
        time.sleep(1)
        
        # Check if we have mock data for this filename
        if filename in self.mock_documents:
            return {
                'status': 'success',
                'filename': filename,
                'processing_time': 1.2,
                **self.mock_documents[filename]
            }
        
        # For unknown documents, try to detect type from filename
        detected_type = self.detect_type_from_filename(filename)
        mock_data = self.generate_mock_data(detected_type)
        
        return {
            'status': 'success',
            'filename': filename,
            'processing_time': 1.5,
            'type': detected_type,
            'extracted_data': mock_data['data'],
            'calculated_co2_kg': mock_data['co2_kg'],
            'confidence': 0.75  # Lower confidence for non-sample documents
        }
    
    def detect_type_from_filename(self, filename: str) -> str:
        """Detect document type from filename patterns"""
        filename_lower = filename.lower()
        
        if any(keyword in filename_lower for keyword in ['electric', 'power', 'kwh', 'pge', 'utility']):
            return 'electricity_bill'
        elif any(keyword in filename_lower for keyword in ['gas', 'therm', 'heating']):
            return 'gas_bill'
        elif any(keyword in filename_lower for keyword in ['fuel', 'gas_station', 'receipt', 'shell', 'exxon']):
            return 'fuel_receipt'
        elif any(keyword in filename_lower for keyword in ['flight', 'travel', 'airline', 'trip']):
            return 'travel_invoice'
        else:
            return 'unknown'
    
    def generate_mock_data(self, doc_type: str) -> Dict[str, Any]:
        """Generate mock data for detected document types"""
        import random
        
        if doc_type == 'electricity_bill':
            kwh = round(random.uniform(200, 800), 1)
            return {
                'data': {
                    'kwh_usage': kwh,
                    'billing_period': '2025-09-01 to 2025-09-30',
                    'total_cost': round(kwh * 0.12, 2),
                    'utility_company': 'Local Electric Co.'
                },
                'co2_kg': round(kwh * 0.4, 2)
            }
        elif doc_type == 'gas_bill':
            therms = round(random.uniform(15, 40), 1)
            return {
                'data': {
                    'therm_usage': therms,
                    'billing_period': '2025-09-01 to 2025-09-30',
                    'total_cost': round(therms * 1.35, 2),
                    'utility_company': 'Local Gas Co.'
                },
                'co2_kg': round(therms * 5.3, 2)
            }
        elif doc_type == 'fuel_receipt':
            gallons = round(random.uniform(8, 20), 3)
            return {
                'data': {
                    'gallons': gallons,
                    'fuel_type': 'regular',
                    'total_cost': round(gallons * 3.45, 2),
                    'station': 'Gas Station',
                    'date': '2025-09-20'
                },
                'co2_kg': round(gallons * 8.89, 2)
            }
        else:
            return {
                'data': {'note': 'Could not extract specific data'},
                'co2_kg': 0.0
            }

# Initialize FastAPI app and processor
app = FastAPI(title="CarbonTrack PDF Import API")
processor = MockPDFProcessor()

# In-memory storage for demo (use database in production)
processing_results = {}

@app.post("/api/v1/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    organization_id: str = "demo-org",
    department: str = "Operations"
):
    """Upload and process PDF documents"""
    
    results = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': 'Only PDF files are supported'
            })
            continue
        
        if file.size and file.size > 10 * 1024 * 1024:  # 10MB limit
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': 'File too large (max 10MB)'
            })
            continue
        
        try:
            # Read file content
            content = await file.read()
            
            # Process document
            result = processor.process_document(file.filename, content)
            
            # Add metadata
            processing_id = f"proc_{len(processing_results) + 1}"
            result.update({
                'processing_id': processing_id,
                'organization_id': organization_id,
                'department': department,
                'upload_timestamp': datetime.utcnow().isoformat(),
                'status': 'completed'
            })
            
            # Store result
            processing_results[processing_id] = result
            
            results.append({
                'filename': file.filename,
                'processing_id': processing_id,
                'status': 'completed',
                'document_type': result['type'],
                'co2_kg': result['calculated_co2_kg'],
                'extracted_fields': len(result['extracted_data'])
            })
            
        except Exception as e:
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': str(e)
            })
    
    return {
        'total_files': len(files),
        'successful': len([r for r in results if r['status'] == 'completed']),
        'failed': len([r for r in results if r['status'] == 'error']),
        'results': results
    }

@app.get("/api/v1/documents/processing/{processing_id}")
async def get_processing_result(processing_id: str):
    """Get detailed processing results"""
    
    if processing_id not in processing_results:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    result = processing_results[processing_id]
    
    return {
        'processing_id': processing_id,
        'status': result['status'],
        'document_info': {
            'filename': result['filename'],
            'upload_timestamp': result['upload_timestamp'],
            'processing_time_seconds': result.get('processing_time', 0)
        },
        'classification': {
            'document_type': result['type'],
            'confidence': result.get('confidence', 1.0)
        },
        'extracted_data': result['extracted_data'],
        'carbon_calculation': {
            'total_co2_kg': result['calculated_co2_kg'],
            'calculation_method': 'Standard emission factors',
            'verified': False
        },
        'organization_info': {
            'organization_id': result['organization_id'],
            'department': result['department']
        }
    }

@app.get("/api/v1/documents/list")
async def list_processed_documents(organization_id: str = "demo-org"):
    """List all processed documents for an organization"""
    
    org_documents = [
        {
            'processing_id': pid,
            'filename': result['filename'],
            'document_type': result['type'],
            'co2_kg': result['calculated_co2_kg'],
            'upload_date': result['upload_timestamp'],
            'department': result['department'],
            'status': result['status']
        }
        for pid, result in processing_results.items()
        if result['organization_id'] == organization_id
    ]
    
    # Calculate summary statistics
    total_documents = len(org_documents)
    total_co2 = sum(doc['co2_kg'] for doc in org_documents)
    
    document_types = {}
    for doc in org_documents:
        doc_type = doc['document_type']
        if doc_type not in document_types:
            document_types[doc_type] = {'count': 0, 'co2_kg': 0}
        document_types[doc_type]['count'] += 1
        document_types[doc_type]['co2_kg'] += doc['co2_kg']
    
    return {
        'organization_id': organization_id,
        'summary': {
            'total_documents': total_documents,
            'total_co2_kg': round(total_co2, 2),
            'document_types': document_types
        },
        'documents': org_documents
    }

@app.post("/api/v1/documents/{processing_id}/verify")
async def verify_document_data(
    processing_id: str,
    corrections: Dict[str, Any]
):
    """Verify and correct extracted document data"""
    
    if processing_id not in processing_results:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = processing_results[processing_id]
    
    # Apply corrections to extracted data
    for field, value in corrections.items():
        if field in result['extracted_data']:
            result['extracted_data'][field] = value
    
    # Recalculate CO2 based on corrected data
    doc_type = result['type']
    extracted_data = result['extracted_data']
    
    if doc_type == 'electricity_bill' and 'kwh_usage' in extracted_data:
        new_co2 = extracted_data['kwh_usage'] * 0.4
    elif doc_type == 'gas_bill' and 'therm_usage' in extracted_data:
        new_co2 = extracted_data['therm_usage'] * 5.3
    elif doc_type == 'fuel_receipt' and 'gallons' in extracted_data:
        new_co2 = extracted_data['gallons'] * 8.89
    else:
        new_co2 = result['calculated_co2_kg']
    
    result['calculated_co2_kg'] = round(new_co2, 2)
    result['verified'] = True
    result['verification_timestamp'] = datetime.utcnow().isoformat()
    
    return {
        'processing_id': processing_id,
        'status': 'verified',
        'corrections_applied': len(corrections),
        'new_co2_kg': result['calculated_co2_kg'],
        'verification_timestamp': result['verification_timestamp']
    }

@app.get("/api/v1/documents/sample-data")
async def create_sample_documents():
    """Create sample documents for testing"""
    
    sample_docs = [
        {
            'filename': 'electricity_bill_sample.pdf',
            'type': 'electricity_bill',
            'co2_kg': 180.2
        },
        {
            'filename': 'gas_bill_sample.pdf', 
            'type': 'gas_bill',
            'co2_kg': 134.09
        },
        {
            'filename': 'fuel_receipt_sample.pdf',
            'type': 'fuel_receipt', 
            'co2_kg': 110.74
        }
    ]
    
    # Create sample processing results
    for i, doc in enumerate(sample_docs):
        processing_id = f"sample_{i+1}"
        result = processor.process_document(doc['filename'], b"mock_content")
        result.update({
            'processing_id': processing_id,
            'organization_id': 'demo-org',
            'department': 'Sample Data',
            'upload_timestamp': datetime.utcnow().isoformat(),
            'status': 'completed'
        })
        processing_results[processing_id] = result
    
    return {
        'message': 'Sample documents created',
        'sample_documents': sample_docs,
        'total_sample_co2_kg': sum(doc['co2_kg'] for doc in sample_docs)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CarbonTrack PDF Import Service...")
    print("📄 Upload PDFs at: http://localhost:8001/docs")
    print("📊 Sample documents endpoint: http://localhost:8001/api/v1/documents/sample-data")
    uvicorn.run(app, host="0.0.0.0", port=8001)