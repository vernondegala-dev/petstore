import pytest

@pytest.mark.user
class TestUser:
    def test_create_user(self, api_client):
        user_data = {
            "id": 101,
            "username": "testuser1",
            "firstName": "Test",
            "lastName": "User",
            "email": "testuser1@example.com",
            "password": "password123",
            "phone": "1234567890",
            "userStatus": 1
        }
        response = api_client.create_user(user_data)
        assert response.status_code == 200

    def test_get_user_by_name(self, api_client):
        username = "testuser1"
        response = api_client.get_user_by_name(username)
        assert response.status_code == 200
        assert response.json()["username"] == username

    def test_user_login(self, api_client):
        response = api_client.login_user("testuser1", "password123")
        assert response.status_code == 200
        assert "logged in user session" in response.json()["message"]

    def test_user_logout(self, api_client):
        response = api_client.logout_user()
        assert response.status_code == 200
        assert response.json()["message"] == "ok"

    def test_update_user(self, api_client):
        username = "testuser1"
        updated_data = {
            "id": 101,
            "username": username,
            "firstName": "Updated",
            "lastName": "User",
            "email": "updated@example.com"
        }
        response = api_client.update_user(username, updated_data)
        assert response.status_code == 200
        
        # Verify
        get_response = api_client.get_user_by_name(username)
        assert get_response.json()["firstName"] == "Updated"

    def test_delete_user(self, api_client):
        username = "testuser_delete"
        api_client.create_user({"username": username})
        
        response = api_client.delete_user(username)
        assert response.status_code == 200
        
        # Verify
        get_response = api_client.get_user_by_name(username)
        assert get_response.status_code == 404
