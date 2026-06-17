from locust import HttpUser, task, between, events
import random
import uuid
import logging
import os
from prometheus_client import generate_latest, Gauge, REGISTRY
from gevent import pywsgi
import gevent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Prometheus Metrics (Gauges are better for syncing cumulative stats) ---
# We use Gauges so the Master can 'set' them to the aggregate totals reported by workers
REQUEST_TOTAL = Gauge('locust_requests_total', 'Total requests', ['method', 'name', 'status'])
AVG_RESPONSE_TIME = Gauge('locust_avg_response_time_ms', 'Average response time in ms', ['method', 'name'])
CURRENT_RPS = Gauge('locust_rps', 'Current requests per second', ['method', 'name'])
USER_COUNT = Gauge('locust_users', 'Number of active users')

def metrics_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')]
    start_response(status, headers)
    yield generate_latest(REGISTRY)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if environment.web_ui:
        port = int(os.getenv("METRICS_PORT", 9191))
        logger.info(f"Starting Master Prometheus Exporter on port {port}...")
        server = pywsgi.WSGIServer(('0.0.0.0', port), metrics_app, log=None)
        gevent.spawn(server.serve_forever)

        def stats_poller():
            """Polls the global stats object on the Master to update Prometheus metrics."""
            while True:
                if environment.runner:
                    # 1. Sync User Count
                    USER_COUNT.set(environment.runner.user_count)
                    
                    # 2. Sync Global Stats
                    for stats_entry in environment.runner.stats.entries.values():
                        # Extract labels
                        m = stats_entry.method
                        n = stats_entry.name
                        
                        # Set Request Totals (Success and Failure)
                        REQUEST_TOTAL.labels(method=m, name=n, status="success").set(stats_entry.num_requests)
                        REQUEST_TOTAL.labels(method=m, name=n, status="failure").set(stats_entry.num_failures)
                        
                        # Set Performance Metrics
                        AVG_RESPONSE_TIME.labels(method=m, name=n).set(stats_entry.avg_response_time)
                        CURRENT_RPS.labels(method=m, name=n).set(stats_entry.total_rps)
                        
                gevent.sleep(2)

        gevent.spawn(stats_poller)

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        self.my_pet_ids = []
        self.add_pet()

    @task(3)
    def find_pets_by_status(self):
        self.client.get("/v2/pet/findByStatus?status=available", name="/pet/findByStatus")

    @task(1)
    def add_pet(self):
        pet_id = int(uuid.uuid4().int >> 96)
        payload = {"id": pet_id, "name": f"LocustPet_{pet_id}", "photoUrls": [], "status": "available"}
        with self.client.post("/v2/pet", json=payload, name="/pet", catch_response=True) as response:
            if response.status_code == 200:
                self.my_pet_ids.append(pet_id)
                response.success()
            else:
                response.failure(f"Add failed: {response.status_code}")

    @task(2)
    def get_pet_by_id(self):
        pet_id = random.choice(self.my_pet_ids) if self.my_pet_ids else 1
        url = "/v2/pet/" + str(pet_id)
        with self.client.get(url, name="/pet/{petId}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get {pet_id} failed: {response.status_code}")

    @task(1)
    def get_inventory(self):
        self.client.get("/v2/store/inventory", name="/store/inventory")
