import requests
import os

class PetstoreClient:
    def __init__(self, base_url="https://petstore.swagger.io/v2"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "api_key": os.getenv("API_KEY", "special-key")
        }

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        return response

    # Pet Endpoints
    def add_pet(self, data):
        return self._request("POST", "/pet", json=data)

    def update_pet(self, data):
        return self._request("PUT", "/pet", json=data)

    def get_pet_by_id(self, pet_id):
        return self._request("GET", f"/pet/{pet_id}")

    def find_pets_by_status(self, status):
        return self._request("GET", "/pet/findByStatus", params={"status": status})

    def delete_pet(self, pet_id):
        return self._request("DELETE", f"/pet/{pet_id}")

    # Store Endpoints
    def get_inventory(self):
        return self._request("GET", "/store/inventory")

    def place_order(self, data):
        return self._request("POST", "/store/order", json=data)

    def get_order_by_id(self, order_id):
        return self._request("GET", f"/store/order/{order_id}")

    def delete_order(self, order_id):
        return self._request("DELETE", f"/store/order/{order_id}")

    # User Endpoints
    def create_user(self, data):
        return self._request("POST", "/user", json=data)

    def get_user_by_name(self, username):
        return self._request("GET", f"/user/{username}")

    def update_user(self, username, data):
        return self._request("PUT", f"/user/{username}", json=data)

    def delete_user(self, username):
        return self._request("DELETE", f"/user/{username}")

    def login_user(self, username, password):
        return self._request("GET", "/user/login", params={"username": username, "password": password})

    def logout_user(self):
        return self._request("GET", "/user/logout")
