# Petstore API Test Automation Framework

This project provides a comprehensive test automation and performance testing framework for the Petstore API.

## Features
- **Pytest Framework**: Comprehensive API tests for Pet, Store, and User modules.
- **Locust Performance Testing**: Scalable performance tests with Prometheus integration.
- **Infrastructure as Code**: Dockerized components and Kubernetes manifests.
- **CI/CD**: Jenkins pipeline for automated build, test, and deployment.

## Project Structure
- `tests/`: Pytest API test scenarios.
- `performance/`: Locustfile for performance testing.
- `infrastructure/`:
  - `docker/`: Dockerfiles for Pytest and Locust.
  - `k8s/`: Kubernetes manifests for deployment.
  - `jenkins/`: Jenkinsfile for CI/CD.

## How to Run Locally

### Pytest
1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest tests/ --html=report.html`

### Locust
1. Run Locust: `locust -f performance/locustfile.py --host=https://petstore.swagger.io`
2. Open `http://localhost:8089` to start the test.

## Monitoring & Visualization (Prometheus & Grafana)

The performance tests export metrics to Prometheus, which are then visualized in Grafana.

### 1. Deploy Monitoring Stack
```bash
# Deploy Prometheus
kubectl apply -f infrastructure/k8s/prometheus-deployment.yaml

# Deploy Grafana
kubectl apply -f infrastructure/k8s/grafana-deployment.yaml
```

### 2. Configure Grafana
1.  Access Grafana via the LoadBalancer IP on port `3000` (Default login: `admin/admin`).
2.  **Add Data Source:**
    *   Name: `Prometheus`
    *   URL: `http://prometheus:9090`
3.  **Import Dashboard:**
    *   Go to **Dashboards -> Import**.
    *   Use Dashboard ID `12020` (standard Locust dashboard) or upload a custom JSON.

## CI/CD with Jenkins

The project includes a `Jenkinsfile` located in `infrastructure/jenkins/` to automate the build, test, and deployment process.

### 1. Prerequisites
- **Jenkins Plugins:** `Pipeline`, `Git`, `Docker Pipeline`, `HTML Publisher`.
- **System Requirements:** 
    - `docker` installed on the Jenkins agent.
    - `kubectl` configured with access to your Kubernetes cluster.
    - Permission to push images to your Docker registry.

### 2. Pipeline Configuration
1.  **Create a New Job:** Select "Pipeline" in Jenkins.
2.  **Pipeline Definition:** Select "Pipeline script from SCM".
    - **SCM:** Git
    - **Repository URL:** [Your Repository URL]
    - **Script Path:** `infrastructure/jenkins/Jenkinsfile`
3.  **Environment Variables:** Edit the `Jenkinsfile` or set Jenkins environment variables for:
    - `DOCKER_REGISTRY`: Your private or public registry (e.g., `my-docker-hub-user`).

### 3. Pipeline Stages
- **Checkout:** Clones the repository.
- **Build Images:** Builds Docker images for both Pytest (API tests) and Locust (performance).
- **API Tests (Pytest):** Runs functional tests in a container and publishes an HTML report.
- **Deploy Performance (K8s):** Updates the Kubernetes manifests with the new image tags and deploys the Locust cluster.

### 4. Viewing Results
- Functional test reports are available in the **"Pytest API Report"** link on the Jenkins job sidebar.
- Performance metrics can be viewed in **Grafana** once the deployment stage is complete.
