from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities_returns_activity_data():
    # Arrange
    # No special setup needed; the app starts with the default in-memory activities.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success_for_new_student():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@example.com"

    # Ensure the email is not already present in the in-memory list for this run.
    existing = client.get("/activities").json()[activity_name]["participants"]
    if email in existing:
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]

    # Cleanup for later tests.
    client.delete(f"/activities/{activity_name}/unregister?email={email}")


def test_signup_rejects_duplicate_email():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@example.com"

    # Make sure the email starts as absent.
    existing = client.get("/activities").json()[activity_name]["participants"]
    if email in existing:
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

    # Cleanup
    client.delete(f"/activities/{activity_name}/unregister?email={email}")


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "removeme@example.com"

    # Ensure the test starts from a clean state.
    existing = client.get("/activities").json()[activity_name]["participants"]
    if email in existing:
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unknown_activity_returns_404():
    # Arrange
    activity_name = "Does Not Exist"
    email = "someone@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
