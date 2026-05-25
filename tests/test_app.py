import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client_with_fresh_activities():
    """Fixture that provides a TestClient and resets activities before/after each test."""
    # Arrange: Make a deep copy of original activities
    original_activities = copy.deepcopy(activities)
    
    yield TestClient(app)
    
    # Restore activities after test
    activities.clear()
    activities.update(original_activities)


def test_get_activities(client_with_fresh_activities):
    """Test: GET /activities returns 200 with activity data"""
    # Arrange
    client = client_with_fresh_activities
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_new_participant(client_with_fresh_activities):
    """Test: POST /activities/{activity}/signup successfully registers participant"""
    # Arrange
    client = client_with_fresh_activities
    activity_name = "Chess Club"
    email = "test.user@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify participant was added
    activities_data = client.get("/activities").json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_duplicate_participant(client_with_fresh_activities):
    """Test: POST /activities/{activity}/signup rejects duplicate signup"""
    # Arrange
    client = client_with_fresh_activities
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_participant(client_with_fresh_activities):
    """Test: DELETE /activities/{activity}/participants removes participant"""
    # Arrange
    client = client_with_fresh_activities
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Verify participant is present before deletion
    activities_before = client.get("/activities").json()
    assert email in activities_before[activity_name]["participants"]
    
    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    
    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    
    # Verify participant was removed
    activities_after = client.get("/activities").json()
    assert email not in activities_after[activity_name]["participants"]


def test_unregister_missing_participant(client_with_fresh_activities):
    """Test: DELETE /activities/{activity}/participants returns 404 for missing participant"""
    # Arrange
    client = client_with_fresh_activities
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]
