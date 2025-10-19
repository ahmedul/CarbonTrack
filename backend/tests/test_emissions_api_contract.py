import os
from fastapi.testclient import TestClient

# Ensure debug so mock tokens are accepted
os.environ["DEBUG"] = "true"

from app.main import app  # noqa: E402
from app.services.dynamodb_service import dynamodb_service  # noqa: E402


client = TestClient(app)


def test_post_and_get_emissions_contract(monkeypatch):
    # Mock create_carbon_emission
    async def mock_create(emission_data):
        return {
            "success": True,
            "entry_id": "test-entry-1",
            "timestamp": "2025-10-18T12:00:00Z",
        }

    # Mock get_user_emissions to return one item resembling DynamoDB item
    async def mock_get(user_id: str, start_date=None, end_date=None, limit: int = 50):
        return [
            {
                "userId": user_id,
                "timestamp": "2025-10-18T12:00:00Z",
                "entry_id": "test-entry-1",
                "date": "2025-10-18",
                "category": "transportation",
                "activity": "car_gasoline_medium",
                "amount": 25.0,
                "unit": "km",
                "description": "Test drive",
                "co2_equivalent": 5.0,
                "emission_factor": 0.2,
            }
        ]

    monkeypatch.setattr(dynamodb_service, "create_carbon_emission", mock_create)
    monkeypatch.setattr(dynamodb_service, "get_user_emissions", mock_get)

    headers = {"Authorization": "Bearer mock_alice"}

    # POST new emission
    payload = {
        "date": "2025-10-18",
        "category": "transportation",
        "activity": "car_gasoline_medium",
        "amount": 25.0,
        "unit": "km",
        "description": "Test drive"
    }

    resp = client.post("/api/v1/carbon-emissions/", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data.get("success") is True
    assert "data" in data and data["data"].get("emission_id") == "test-entry-1"

    # GET emissions and verify contract
    resp2 = client.get("/api/v1/carbon-emissions/", headers=headers)
    assert resp2.status_code == 200, resp2.text
    body = resp2.json()
    assert body.get("success") is True
    assert "data" in body
    d = body["data"]
    assert isinstance(d.get("emissions"), list)
    assert d.get("total_emissions") is not None
    assert d.get("monthly_emissions") is not None
    assert d.get("goal_progress") is not None
