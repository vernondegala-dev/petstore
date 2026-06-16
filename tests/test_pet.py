import pytest
import uuid

@pytest.mark.pet
class TestPet:
    def test_add_new_pet(self, api_client):
        pet_id = int(uuid.uuid4().int >> 96)
        data = {
            "id": pet_id,
            "category": {"id": 1, "name": "Dogs"},
            "name": "Sparky",
            "photoUrls": ["http://example.com/sparky.jpg"],
            "tags": [{"id": 1, "name": "tag1"}],
            "status": "available"
        }
        response = api_client.add_pet(data)
        assert response.status_code == 200
        assert response.json()["name"] == "Sparky"
        assert response.json()["id"] == pet_id

    def test_get_pet_by_id(self, api_client):
        # First ensure a pet exists
        pet_id = 9922
        api_client.add_pet({"id": pet_id, "name": "Rex", "photoUrls": []})
        
        response = api_client.get_pet_by_id(pet_id)
        assert response.status_code == 200
        assert response.json()["id"] == pet_id

    def test_get_non_existent_pet(self, api_client):
        response = api_client.get_pet_by_id(999999999)
        assert response.status_code == 404

    def test_update_pet(self, api_client):
        pet_id = 9923
        api_client.add_pet({"id": pet_id, "name": "Buddy", "photoUrls": [], "status": "available"})
        
        updated_data = {
            "id": pet_id,
            "name": "Buddy-Updated",
            "photoUrls": [],
            "status": "sold"
        }
        response = api_client.update_pet(updated_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Buddy-Updated"
        assert response.json()["status"] == "sold"

    def test_find_pets_by_status(self, api_client):
        response = api_client.find_pets_by_status("available")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_pet(self, api_client):
        pet_id = 9924
        api_client.add_pet({"id": pet_id, "name": "To-Be-Deleted", "photoUrls": []})
        
        response = api_client.delete_pet(pet_id)
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = api_client.get_pet_by_id(pet_id)
        assert get_response.status_code == 404
