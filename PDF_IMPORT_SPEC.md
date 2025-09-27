# 📄 PDF Data Import Technical Specification

## Overview
The PDF Data Import feature enables automated extraction and processing of carbon-relevant data from various document types using OCR, machine learning classification, and intelligent data parsing.

## Technical Architecture

### Core Components

#### 1. Document Upload Service
```python
# FastAPI endpoint for document upload
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from typing import List
import asyncio

app = FastAPI()

@app.post("/api/v1/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks,
    organization_id: str,
    user_id: str
):
    """Upload multiple PDF documents for processing"""
    
    upload_results = []
    for file in files:
        # Validate file type and size
        if not file.filename.endswith('.pdf'):
            continue
        
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            continue
            
        # Save file temporarily
        file_path = await save_uploaded_file(file)
        
        # Queue for background processing
        background_tasks.add_task(
            process_pdf_document,
            file_path=file_path,
            organization_id=organization_id,
            user_id=user_id,
            original_filename=file.filename
        )
        
        upload_results.append({
            "filename": file.filename,
            "status": "queued",
            "processing_id": generate_processing_id()
        })
    
    return {"uploaded_files": upload_results}
```

#### 2. OCR Processing Engine
```python
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

class OCRProcessor:
    def __init__(self):
        # Configure Tesseract for better accuracy
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-$€£¥ '
        
    def preprocess_image(self, image):
        """Improve image quality for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Threshold to binary
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return Image.fromarray(binary)
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using OCR"""
        try:
            # Convert PDF pages to images
            pages = convert_from_path(pdf_path, dpi=300)
            
            extracted_text = []
            for page_num, page in enumerate(pages):
                # Preprocess image for better OCR
                processed_image = self.preprocess_image(page)
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(
                    processed_image, 
                    config=self.ocr_config
                )
                
                # Extract structured data (tables, key-value pairs)
                structured_data = self.extract_structured_data(processed_image)
                
                extracted_text.append({
                    'page': page_num + 1,
                    'text': text.strip(),
                    'structured_data': structured_data,
                    'confidence': self.calculate_confidence(text)
                })
            
            return extracted_text
            
        except Exception as e:
            raise ProcessingError(f"OCR extraction failed: {str(e)}")
    
    def extract_structured_data(self, image):
        """Extract tables and structured data from image"""
        # Use pytesseract to get bounding boxes and data
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Group text into potential table structures
        tables = self.detect_tables(data)
        key_value_pairs = self.detect_key_value_pairs(data)
        
        return {
            'tables': tables,
            'key_value_pairs': key_value_pairs
        }
```

#### 3. Document Classification ML Model
```python
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import re

class DocumentClassifier:
    def __init__(self, model_path='models/document_classifier.pkl'):
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(model_path.replace('.pkl', '_vectorizer.pkl'))
        
        # Document type definitions
        self.document_types = {
            'electricity_bill': {
                'keywords': ['kwh', 'kilowatt', 'electric', 'power', 'utility', 'meter reading'],
                'patterns': [r'\d+\.?\d*\s*kwh', r'meter\s*#?\s*\d+'],
                'carbon_fields': ['kwh_usage', 'billing_period', 'meter_number']
            },
            'gas_bill': {
                'keywords': ['therm', 'natural gas', 'gas usage', 'btu', 'cubic feet'],
                'patterns': [r'\d+\.?\d*\s*therm', r'\d+\.?\d*\s*ccf', r'\d+\.?\d*\s*mcf'],
                'carbon_fields': ['therm_usage', 'gas_usage_ccf', 'billing_period']
            },
            'fuel_receipt': {
                'keywords': ['gasoline', 'diesel', 'fuel', 'gallons', 'liters', 'gas station'],
                'patterns': [r'\d+\.?\d*\s*gal', r'\d+\.?\d*\s*l', r'\$\d+\.\d{2}'],
                'carbon_fields': ['fuel_amount', 'fuel_type', 'vehicle_info']
            },
            'travel_invoice': {
                'keywords': ['flight', 'airline', 'hotel', 'car rental', 'mileage', 'travel'],
                'patterns': [r'flight\s*#?\s*\w+', r'\d+\s*miles?', r'\d+\s*km'],
                'carbon_fields': ['distance', 'transport_mode', 'trip_details']
            },
            'sustainability_report': {
                'keywords': ['co2', 'carbon', 'emissions', 'greenhouse gas', 'sustainability', 'scope'],
                'patterns': [r'\d+\.?\d*\s*tonnes?\s*co2', r'scope\s*[123]', r'\d+\.?\d*\s*kg\s*co2'],
                'carbon_fields': ['total_emissions', 'emission_scopes', 'reporting_period']
            }
        }
    
    def classify_document(self, text):
        """Classify document type using ML model and rule-based approach"""
        
        # ML-based classification
        text_vector = self.vectorizer.transform([text])
        ml_prediction = self.model.predict(text_vector)[0]
        ml_confidence = max(self.model.predict_proba(text_vector)[0])
        
        # Rule-based classification for validation
        rule_based_results = []
        text_lower = text.lower()
        
        for doc_type, config in self.document_types.items():
            score = 0
            
            # Keyword matching
            for keyword in config['keywords']:
                if keyword in text_lower:
                    score += 1
            
            # Pattern matching
            for pattern in config['patterns']:
                matches = re.findall(pattern, text_lower)
                score += len(matches) * 2  # Patterns weighted higher
            
            if score > 0:
                rule_based_results.append((doc_type, score))
        
        # Combine ML and rule-based results
        rule_based_results.sort(key=lambda x: x[1], reverse=True)
        
        final_classification = {
            'ml_prediction': ml_prediction,
            'ml_confidence': ml_confidence,
            'rule_based_top': rule_based_results[0] if rule_based_results else None,
            'final_type': None,
            'confidence': 0
        }
        
        # Decision logic
        if ml_confidence > 0.8:
            final_classification['final_type'] = ml_prediction
            final_classification['confidence'] = ml_confidence
        elif rule_based_results and rule_based_results[0][1] >= 3:
            final_classification['final_type'] = rule_based_results[0][0]
            final_classification['confidence'] = min(rule_based_results[0][1] / 10, 0.9)
        else:
            final_classification['final_type'] = 'unknown'
            final_classification['confidence'] = 0.3
        
        return final_classification
```

#### 4. Carbon Data Parser
```python
import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

class CarbonDataParser:
    def __init__(self):
        self.parsing_rules = {
            'electricity_bill': {
                'kwh_usage': [
                    r'(\d+(?:\.\d+)?)\s*kwh',
                    r'usage:?\s*(\d+(?:\.\d+)?)',
                    r'total\s*kwh:?\s*(\d+(?:\.\d+)?)'
                ],
                'billing_period': [
                    r'billing\s*period:?\s*(\d{1,2}\/\d{1,2}\/\d{4})\s*-\s*(\d{1,2}\/\d{1,2}\/\d{4})',
                    r'service\s*from:?\s*(\d{1,2}\/\d{1,2}\/\d{4})\s*to:?\s*(\d{1,2}\/\d{1,2}\/\d{4})'
                ],
                'cost': [
                    r'\$(\d+(?:\.\d{2})?)',
                    r'total\s*amount:?\s*\$(\d+(?:\.\d{2})?)'
                ]
            },
            'gas_bill': {
                'therm_usage': [
                    r'(\d+(?:\.\d+)?)\s*therms?',
                    r'usage:?\s*(\d+(?:\.\d+)?)\s*therms?'
                ],
                'ccf_usage': [
                    r'(\d+(?:\.\d+)?)\s*ccf',
                    r'(\d+(?:\.\d+)?)\s*hundred\s*cubic\s*feet'
                ]
            },
            'fuel_receipt': {
                'gallons': [
                    r'(\d+(?:\.\d{3})?)\s*gal',
                    r'gallons:?\s*(\d+(?:\.\d{3})?)'
                ],
                'fuel_type': [
                    r'(regular|premium|diesel|unleaded)',
                    r'grade:?\s*(regular|premium|diesel|unleaded)'
                ],
                'total_cost': [
                    r'total:?\s*\$(\d+(?:\.\d{2})?)',
                    r'\$(\d+(?:\.\d{2})?)(?:\s*total)?'
                ]
            }
        }
    
    def parse_carbon_data(self, text: str, document_type: str) -> Dict:
        """Parse carbon-relevant data from document text"""
        
        if document_type not in self.parsing_rules:
            return {'error': f'Unknown document type: {document_type}'}
        
        rules = self.parsing_rules[document_type]
        extracted_data = {}
        
        text_lower = text.lower()
        
        for field, patterns in rules.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    # Handle different match types
                    if len(matches[0]) == 2 if isinstance(matches[0], tuple) else False:
                        # Date ranges
                        extracted_data[field] = {
                            'start_date': matches[0][0],
                            'end_date': matches[0][1]
                        }
                    else:
                        # Single values
                        value = matches[0] if isinstance(matches[0], str) else matches[0]
                        extracted_data[field] = self.convert_to_appropriate_type(value, field)
                    break
        
        # Calculate carbon footprint
        carbon_footprint = self.calculate_carbon_footprint(extracted_data, document_type)
        extracted_data['calculated_co2_kg'] = carbon_footprint
        
        return extracted_data
    
    def convert_to_appropriate_type(self, value: str, field: str):
        """Convert extracted string to appropriate data type"""
        
        # Numeric fields
        if any(keyword in field for keyword in ['usage', 'cost', 'gallons', 'amount']):
            try:
                return float(value.replace(',', ''))
            except ValueError:
                return value
        
        # Date fields
        if 'date' in field:
            try:
                return datetime.strptime(value, '%m/%d/%Y').isoformat()
            except ValueError:
                return value
        
        return value
    
    def calculate_carbon_footprint(self, data: Dict, document_type: str) -> float:
        """Calculate carbon footprint from extracted data"""
        
        emission_factors = {
            'electricity_kwh': 0.4,  # kg CO2 per kWh (US average)
            'natural_gas_therm': 5.3,  # kg CO2 per therm
            'gasoline_gallon': 8.89,  # kg CO2 per gallon
            'diesel_gallon': 10.15  # kg CO2 per gallon
        }
        
        if document_type == 'electricity_bill' and 'kwh_usage' in data:
            return data['kwh_usage'] * emission_factors['electricity_kwh']
        
        elif document_type == 'gas_bill' and 'therm_usage' in data:
            return data['therm_usage'] * emission_factors['natural_gas_therm']
        
        elif document_type == 'fuel_receipt':
            if 'gallons' in data:
                fuel_type = data.get('fuel_type', 'regular')
                factor_key = 'diesel_gallon' if fuel_type == 'diesel' else 'gasoline_gallon'
                return data['gallons'] * emission_factors[factor_key]
        
        return 0.0
```

### Database Schema for PDF Processing

```sql
-- Document processing tables
CREATE TABLE document_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status ENUM('queued', 'processing', 'completed', 'failed'),
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE document_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_upload_id UUID REFERENCES document_uploads(id),
    document_type VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2),
    ml_prediction VARCHAR(50),
    ml_confidence DECIMAL(3,2),
    rule_based_prediction VARCHAR(50),
    rule_based_score INTEGER,
    classification_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE extracted_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_upload_id UUID REFERENCES document_uploads(id),
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT,
    field_type VARCHAR(20), -- 'string', 'number', 'date', 'boolean'
    confidence_score DECIMAL(3,2),
    extraction_method VARCHAR(20), -- 'ocr', 'pattern', 'ml'
    page_number INTEGER
);

CREATE TABLE carbon_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_upload_id UUID REFERENCES document_uploads(id),
    calculated_co2_kg DECIMAL(10,3),
    calculation_method VARCHAR(50),
    emission_factors_used JSONB,
    calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN DEFAULT FALSE,
    verification_user_id UUID REFERENCES users(id),
    verification_timestamp TIMESTAMP
);
```

### API Endpoints

```python
# Complete API implementation
@app.get("/api/v1/documents/processing-status/{processing_id}")
async def get_processing_status(processing_id: str):
    """Get the status of document processing"""
    
    document = await get_document_by_processing_id(processing_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "processing_id": processing_id,
        "status": document.processing_status,
        "progress": calculate_progress_percentage(document),
        "estimated_completion": estimate_completion_time(document),
        "results": await get_processing_results(document.id) if document.processing_status == 'completed' else None
    }

@app.get("/api/v1/documents/{document_id}/results")
async def get_document_results(document_id: str, current_user=Depends(get_current_user)):
    """Get processed results for a document"""
    
    document = await get_document_with_results(document_id)
    
    if not document or document.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_info": {
            "filename": document.original_filename,
            "upload_date": document.upload_timestamp,
            "processing_time": calculate_processing_time(document)
        },
        "classification": {
            "document_type": document.classification.document_type,
            "confidence": document.classification.confidence_score
        },
        "extracted_data": format_extracted_data(document.extracted_data),
        "carbon_footprint": {
            "total_co2_kg": document.carbon_calculation.calculated_co2_kg,
            "calculation_method": document.carbon_calculation.calculation_method,
            "emission_factors": document.carbon_calculation.emission_factors_used
        },
        "verification_status": document.carbon_calculation.verified
    }

@app.post("/api/v1/documents/{document_id}/verify")
async def verify_extracted_data(
    document_id: str,
    verification_data: DocumentVerificationRequest,
    current_user=Depends(get_current_user)
):
    """Verify and correct extracted data"""
    
    # Update extracted data with user corrections
    await update_extracted_data(document_id, verification_data.corrections)
    
    # Recalculate carbon footprint with corrected data
    new_calculation = await recalculate_carbon_footprint(
        document_id, 
        verification_data.corrections
    )
    
    # Mark as verified
    await mark_as_verified(document_id, current_user.id)
    
    return {
        "status": "verified",
        "updated_co2_kg": new_calculation.calculated_co2_kg,
        "verification_timestamp": datetime.utcnow().isoformat()
    }
```

This comprehensive PDF import system provides enterprise-grade document processing capabilities with high accuracy OCR, intelligent classification, and automated carbon footprint calculation.