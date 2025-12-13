from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_create_report():
    response = client.post(
        "/api/v1/csrd/reports",
        json={
            "company_name": "Test Corp",
            "reporting_year": 2024,
            "description": "Test Report"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "Test Corp"
    assert "id" in data
    return data["id"]

def test_get_reports():
    # Create one first
    client.post(
        "/api/v1/csrd/reports",
        json={"company_name": "List Test", "reporting_year": 2024}
    )
    
    response = client.get("/api/v1/csrd/reports")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_metric():
    # Create report
    create_res = client.post(
        "/api/v1/csrd/reports",
        json={"company_name": "Metric Test", "reporting_year": 2024}
    )
    report_id = create_res.json()["id"]
    
    # Update metric E1-1
    response = client.put(
        f"/api/v1/csrd/reports/{report_id}/standards/E1/metrics/E1-1",
        params={"value": 100.5, "status": "complete"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify update
    e1 = next(s for s in data["standards"] if s["code"] == "E1")
    m1 = next(m for m in e1["metrics"] if m["id"] == "E1-1")
    assert m1["value"] == 100.5
    assert m1["status"] == "complete"

def test_generate_pdf():
    # Create report
    create_res = client.post(
        "/api/v1/csrd/reports",
        json={"company_name": "PDF Test", "reporting_year": 2024}
    )
    report_id = create_res.json()["id"]
    
    # Generate PDF
    response = client.post(f"/api/v1/csrd/reports/{report_id}/generate-pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
