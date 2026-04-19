import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    # Arrange: No special setup needed for root endpoint

    # Act: Make GET request to root
    response = client.get("/", follow_redirects=False)

    # Assert: Should redirect to /static/index.html
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange: No special setup needed, activities are in-memory

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Should return 200 and the activities dictionary
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_success():
    # Arrange: Choose an activity and email not already signed up
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_activity_not_found():
    # Arrange: Use a non-existent activity name
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 404 with error detail
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_duplicate():
    # Arrange: Sign up first, then try again
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # First signup

    # Act: Make POST request to signup again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 400 with error detail
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]


def test_unregister_success():
    # Arrange: Sign up first, then unregister
    activity_name = "Gym Class"
    email = "unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})  # Signup

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_unregister_activity_not_found():
    # Arrange: Use a non-existent activity name
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 404 with error detail
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    # Arrange: Try to unregister without signing up first
    activity_name = "Basketball Team"
    email = "notsignedup@mergington.edu"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should return 400 with error detail
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up" in data["detail"]