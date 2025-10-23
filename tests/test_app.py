"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root path redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    assert "index.html" in response.url

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check activity structure
    for name, details in activities.items():
        assert isinstance(name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first available activity
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    # Try signing up
    test_email = "test_student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert test_email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test that duplicate signups are prevented"""
    # Get first available activity
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    # Sign up twice with the same email
    test_email = "duplicate_test@mergington.edu"
    
    # First signup should succeed
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # Get first available activity
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    # First sign up
    test_email = "unregister_test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    
    # Then unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify student is no longer in participants
    response = client.get("/activities")
    activities = response.json()
    assert test_email not in activities[activity_name]["participants"]

def test_unregister_nonexistent():
    """Test unregistering a student that isn't registered"""
    # Get first available activity
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    # Try to unregister a student that isn't registered
    test_email = "nonexistent@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"].lower()