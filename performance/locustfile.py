from locust import HttpUser, task, between, events
# Direct import - will cause crash with clear logs if install is broken
from locust_plugins.listeners.prometheus import PrometheusExporter
import random
import uuid
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # locust-plugins >= 4.0.0 uses this path and handles master/worker internally
    try:
        port = int(os.getenv("METRICS_PORT", 9191))
        logger.info(f"Starting Prometheus Exporter on port {port}...")
        PrometheusExporter(environment, port=port)
        logger.info("Prometheus Exporter successfully initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Prometheus Exporter: {e}")

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)
    created_pet_ids = []

    @task(3)
    def find_pets_by_status(self):
        status = random.choice(["available", "pending", "sold"])
        self.client.get(f"/v2/pet/findByStatus?status={status}", name="/pet/findByStatus")

    @task(1)
    def add_pet(self):
        pet_id = int(uuid.uuid4().int >> 96)
        payload = {"id": pet_id, "name": f"LocustPet_{pet_id}", "photoUrls": [], "status": "available"}
        with self.client.post("/v2/pet", json=payload, name="/pet", catch_response=True) as response:
            if response.status_code == 200:
                self.created_pet_ids.append(pet_id)
                response.success()
            else:
                response.failure(f"Failed to add pet: {response.status_code}")

    @task(2)
    def get_pet_by_id(self):
        pet_id = random.choice(self.created_pet_ids) if self.created_pet_ids else random.randint(1, 100)
        url = f"/v2/pet/{pet_id}"
        with self.client.get(url, name="/pet/{petId}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404 and pet_id not in self.created_pet_ids:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(1)
    def place_order(self):
        pet_id = random.choice(self.created_pet_ids) if self.created_pet_ids else 1
        payload = {"id": random.randint(1, 1000), "petId": pet_id, "quantity": 1, "status": "placed"}
        self.client.post("/v2/store/order", json=payload, name="/store/order")

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory", name="/store/inventory")
