from locust import HttpUser, task, between, events
import random
import uuid
import logging
import os
from prometheus_client import generate_latest, Gauge, Counter, Histogram, REGISTRY
from gevent import pywsgi
import gevent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Native Prometheus Metrics
REQUEST_TIME = Histogram('locust_request_duration_seconds', 'Response time in seconds', ['method', 'name'])
REQUEST_COUNT = Counter('locust_requests_total', 'Total requests', ['method', 'name', 'status'])
USER_COUNT = Gauge('locust_users', 'Number of active users')

def metrics_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')]
    start_response(status, headers)
    yield generate_latest(REGISTRY)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    In distributed mode, this runs on the Master. 
    We listen to stats updates from workers to update our Prometheus gauges.
    """
    if environment.web_ui:
        # 1. Start the Prometheus metrics server
        port = int(os.getenv("METRICS_PORT", 9191))
        logger.info(f"Starting Master Prometheus Exporter on port {port}...")
        server = pywsgi.WSGIServer(('0.0.0.0', port), metrics_app, log=None)
        gevent.spawn(server.serve_forever)

        # 2. Background task to sync user count and stats from the runner
        def stats_poller():
            while True:
                if environment.runner:
                    # Sync User Count
                    USER_COUNT.set(environment.runner.user_count)
                    
                    # Sync Request Stats
                    for stats_entry in environment.runner.stats.entries.values():
                        method = stats_entry.method
                        name = stats_entry.name
                        
                        # Note: Counter in prometheus_client is additive, 
                        # but Locust stats are cumulative. 
                        # We use a trick: set the value to the current total.
                        # Since Counter doesn't have 'set', we'll use the request event instead.
                gevent.sleep(2)

        gevent.spawn(stats_poller)

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """
    This fires on Workers during the test, and on the Master 
    when it receives a report from a worker.
    """
    status = "failure" if exception else "success"
    REQUEST_COUNT.labels(method=request_type, name=name, status=status).inc()
    REQUEST_TIME.labels(method=request_type, name=name).observe(response_time / 1000.0)

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
                response.failure(f"Error {response.status_code}")

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
