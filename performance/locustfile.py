from locust import HttpUser, task, between, events
import random
import uuid
import logging

# Set up logging for locust
logger = logging.getLogger(__name__)

# Robust import for PrometheusExporter
try:
    from locust_plugins.listeners.prometheus import PrometheusExporter
except (ImportError, ModuleNotFoundError):
    try:
        from locust_plugins.listeners import PrometheusExporter
    except (ImportError, ModuleNotFoundError):
        PrometheusExporter = None

# Prometheus Exporter Listener
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if PrometheusExporter and environment.web_ui:
        PrometheusExporter(environment, port=9191)

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)
    
    # Store IDs of pets created during this session to avoid 404s
    created_pet_ids = []

    @task(3)
    def find_pets_by_status(self):
        status = random.choice(["available", "pending", "sold"])
        self.client.get(f"/v2/pet/findByStatus?status={status}", name="/pet/findByStatus")

    @task(1)
    def add_pet(self):
        pet_id = int(uuid.uuid4().int >> 96)
        payload = {
            "id": pet_id,
            "name": f"LocustPet_{pet_id}",
            "photoUrls": ["http://example.com/photo.jpg"],
            "status": "available"
        }
        with self.client.post("/v2/pet", json=payload, name="/pet", catch_response=True) as response:
            if response.status_code == 200:
                self.created_pet_ids.append(pet_id)
                response.success()
            else:
                response.failure(f"Failed to add pet: {response.status_code}")

    @task(2)
    def get_pet_by_id(self):
        # Use a created ID if available, otherwise fallback to a random one (likely to 404)
        if self.created_pet_ids:
            pet_id = random.choice(self.created_pet_ids)
        else:
            pet_id = random.randint(1, 100)
            
        # FIX: Ensure the URL uses the actual variable pet_id
        url = f"/v2/pet/{pet_id}"
        with self.client.get(url, name="/pet/{petId}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # If we used a random ID, 404 is expected behavior
                if pet_id not in self.created_pet_ids:
                    response.success() 
                else:
                    response.failure(f"Created pet {pet_id} not found (404)")
            else:
                response.failure(f"Unexpected status {response.status_code}")

    @task(1)
    def place_order(self):
        order_id = random.randint(100, 1000)
        pet_id = random.choice(self.created_pet_ids) if self.created_pet_ids else 1
        payload = {
            "id": order_id,
            "petId": pet_id,
            "quantity": 1,
            "status": "placed",
            "complete": False
        }
        with self.client.post("/v2/store/order", json=payload, name="/store/order", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to place order: {response.status_code}")

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory", name="/store/inventory")
