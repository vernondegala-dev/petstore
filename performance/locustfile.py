from locust import HttpUser, task, between
import random
import uuid

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def find_pets_by_status(self):
        status = random.choice(["available", "pending", "sold"])
        self.client.get(f"/v2/pet/findByStatus?status={status}")

    @task(2)
    def get_pet_by_id(self):
        pet_id = random.randint(1, 100)
        self.client.get(f"/v2/pet/{pet_id}")

    @task(1)
    def add_pet(self):
        pet_id = int(uuid.uuid4().int >> 96)
        self.client.post("/v2/pet", json={
            "id": pet_id,
            "name": f"LocustPet_{pet_id}",
            "photoUrls": ["http://example.com/photo.jpg"],
            "status": "available"
        })

    @task(1)
    def place_order(self):
        order_id = random.randint(100, 1000)
        self.client.post("/v2/store/order", json={
            "id": order_id,
            "petId": random.randint(1, 10),
            "quantity": 1,
            "status": "placed",
            "complete": False
        })

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory")
