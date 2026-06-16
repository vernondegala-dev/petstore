import pytest

@pytest.mark.store
class TestStore:
    def test_get_inventory(self, api_client):
        response = api_client.get_inventory()
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_place_order(self, api_client):
        order_data = {
            "id": 10,
            "petId": 1,
            "quantity": 1,
            "shipDate": "2023-10-27T10:00:00.000Z",
            "status": "placed",
            "complete": True
        }
        response = api_client.place_order(order_data)
        assert response.status_code == 200
        assert response.json()["id"] == 10
        assert response.json()["status"] == "placed"

    def test_get_order_by_id(self, api_client):
        order_id = 11
        api_client.place_order({"id": order_id, "petId": 1, "quantity": 1})
        
        response = api_client.get_order_by_id(order_id)
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    def test_delete_order(self, api_client):
        order_id = 12
        api_client.place_order({"id": order_id, "petId": 1, "quantity": 1})
        
        response = api_client.delete_order(order_id)
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = api_client.get_order_by_id(order_id)
        assert get_response.status_code == 404
