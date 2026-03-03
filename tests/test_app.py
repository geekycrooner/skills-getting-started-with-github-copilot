from fastapi import status


def test_root_redirect(client):
    # Arrange/Act
    # the TestClient will follow redirects by default, so disable that behaviour
    # to assert the actual status code returned by the endpoint itself.
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    # we expect at least the sample activities defined in src/app.py
    assert "Chess Club" in data


def test_signup_for_existing_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    # second request to ensure participant actually added
    get_resp = client.get("/activities")
    assert email in get_resp.json()[activity]["participants"]


def test_signup_nonexistent_activity(client):
    # Act
    response = client.post("/activities/NotReal/signup?email=test@x.com")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_signup_duplicate(client):
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Programming Class"

    # first signup should succeed
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == status.HTTP_200_OK

    # Act: second signup
    r2 = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert r2.status_code == status.HTTP_400_BAD_REQUEST


def test_remove_participant_success(client):
    # Arrange
    email = "remove@mergington.edu"
    activity = "Gym Class"
    # add participant first
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Removed {email} from {activity}"
    # confirm removal
    get_resp = client.get("/activities")
    assert email not in get_resp.json()[activity]["participants"]


def test_remove_nonexistent_activity(client):
    response = client.delete("/activities/NoSuch/participants?email=foo@bar.com")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_nonexistent_participant(client):
    activity = "Basketball Team"
    response = client.delete(f"/activities/{activity}/participants?email=absent@x.com")
    assert response.status_code == status.HTTP_404_NOT_FOUND
