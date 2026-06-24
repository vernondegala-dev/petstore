# Petstore API Test Automation & Performance Framework

A comprehensive, production-ready framework for testing the [Swagger Petstore API](https://petstore.swagger.io/#/). It features functional test suites, distributed performance load testing, end-to-end monitoring, CI/CD integration, and a cutting-edge **Autonomous AI-Driven QA Testing Agent** powered by Google Gemini.

---

## 🚀 Key Features

*   **Autonomous AI QA Agent:** An intelligent agent utilizing LLM-based tool calling to dynamically explore, test, and validate API endpoints, auto-generating standard Pytest files when bugs or edge cases are identified.
*   **Functional Testing:** A robust Pytest suite covering Pet, Store, and User modules with full test isolation, parallel execution support, and detailed HTML reporting.
*   **Performance Testing:** A distributed Locust cluster configuration (1 Master, 3 Workers) optimized for high-load simulation under Kubernetes.
*   **Native Observability:** Custom gevent-compatible Prometheus exporter integrating directly with Locust to provide real-time, cluster-wide latency and throughput metrics.
*   **Infrastructure as Code (IaC):** Ready-to-use Kubernetes manifests for deploying the Locust cluster, Prometheus monitoring stack, and Grafana visualization dashboards.
*   **CI/CD Pipeline:** Integrated Jenkinsfile defining stages for secure container builds, automated unit/functional tests, and rolling K8s deployments.

---

## 📂 Project Structure

```text
petstore/
├── agents/                  # AI-driven testing agent & runners
│   ├── cli_runner.py        # CLI interface for executing the QA agent
│   └── qa_agent.py          # Core QA agent logic with ReAct and tool-calling
├── api_client/              # Modular API client for Petstore API interactions
│   └── client.py            # Main API client (wrapper for requests)
├── performance/             # Load and performance testing definitions
│   └── locustfile.py        # Gevent-compatible Locust script with custom Prometheus metrics
├── infrastructure/          # Deployment and infrastructure files
│   ├── docker/              # Dockerfiles for Locust and Pytest environments
│   ├── jenkins/             # CI/CD Jenkinsfile
│   └── k8s/                 # Kubernetes manifests for Locust, Prometheus, & Grafana
├── tests/                   # Pytest functional test suites
│   ├── conftest.py          # Pytest configuration and shared fixtures
│   ├── test_agent.py        # Unit tests for the AI QA Agent components
│   ├── test_pet.py          # Functional test cases for the Pet module
│   ├── test_store.py        # Functional test cases for the Store module
│   └── test_user.py         # Functional test cases for the User module
├── pytest.ini               # Pytest configurations and markers
└── requirements.txt         # Project dependencies
```

---

## 🛠️ Setup & Configuration

### 1. Prerequisites
Ensure you have the following installed locally:
*   Python 3.11 or newer
*   `pip` (Python package installer)
*   *Optional:* `kubectl` and a Kubernetes cluster (e.g., Minikube, EKS, GKE) for monitoring/infrastructure deployment.

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
To use the AI-driven QA Testing Agent or configure the API Client, create a `.env` file in the project root:

```ini
# --- Required for AI QA Agent ---
# Provide your Google Gemini API Key
GEMINI_API_KEY="your-gemini-api-key-here"

# --- Optional API Key for Petstore API ---
# Set if you have a custom/authorized Petstore API Key (default is "special-key")
API_KEY="your-petstore-api-key-here"
```

You can also export them directly in your shell:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

---

## 🏃 Execution Guide

### 1. Autonomous AI QA Agent (Google Gemini)
The framework includes an autonomous testing agent that executes natural language objectives. It leverages Google Gemini's tool-calling capabilities to interact with the Petstore API in real time. If it uncovers an issue or wants to establish new test cases, it can automatically write a secure Pytest test to the `tests/` directory.

#### Running the Agent
Run the agent using the interactive CLI runner:
```bash
python agents/cli_runner.py "Verify pet inventory API and place a temporary order to see if inventory updates"
```

#### CLI Parameters & Customization
```bash
python agents/cli_runner.py [OBJECTIVE] [OPTIONS]
```
*   `objective` *(Positional)*: The high-level testing prompt or goal.
*   `--model` *(Optional)*: The Google Gemini model to use (default: `gemini-2.5-flash`).
*   `--base-url` *(Optional)*: Base URL of the Swagger Petstore API (default: `https://petstore.swagger.io/v2`).

#### Core Agent Capabilities
*   **ReAct Loop:** Analyzes responses step-by-step before deciding on the next tool to run.
*   **Automatic Pytest Code Generation:** Uses the specialized tool `write_pytest_test` to automatically write standard Pytest tests (with unique names like `tests/test_agent_*.py` to protect core files) when it identifies regressions.
*   **Report Synthesis:** Generates a structured markdown report displaying status codes, payload analyses, and detailed QA findings.

---

### 2. Functional Testing (Pytest)
Run the automated functional test suite locally to validate API correctness.

#### Run All Tests
```bash
pytest
```

#### Run with Verbose Output and Markers
Filter tests by specific modules (defined in `pytest.ini`):
```bash
# Run Pet API tests only
pytest -m pet -v

# Run Store API tests only
pytest -m store -v

# Run User API tests only
pytest -m user -v
```

#### Run Agent Unit Tests
Verify the agent's logic, mock behaviors, and tools:
```bash
pytest tests/test_agent.py -v
```

#### Generate HTML Reports
Execute the tests and compile a rich HTML report:
```bash
pytest --html=reports/report.html --self-contained-html
```

---

### 3. Performance Testing (Locust)
Simulate realistic load patterns on the Petstore API.

#### Running Locust Locally (GUI Mode)
1.  Start the Locust interface:
    ```bash
    locust -f performance/locustfile.py
    ```
2.  Open your browser and navigate to `http://localhost:8089`.
3.  Configure the number of users, spawn rate, and host (default: `https://petstore.swagger.io/v2`), then click **"Start Swarming"**.

#### Running Locust in Headless Mode (CLI Mode)
To run a quick performance test directly in the terminal without a GUI:
```bash
locust -f performance/locustfile.py --headless -u 10 -r 2 --run-time 1m --host https://petstore.swagger.io/v2
```

---

### 4. Distributed K8s Load Testing & Monitoring

Deploy a scalable load testing framework with real-time Prometheus monitoring and Grafana dashboards in Kubernetes.

#### Deployment Steps
```bash
# Apply Prometheus configuration maps
kubectl apply -f infrastructure/k8s/prometheus-config.yaml

# Deploy Prometheus and Grafana monitoring instances
kubectl apply -f infrastructure/k8s/prometheus-deployment.yaml
kubectl apply -f infrastructure/k8s/grafana-deployment.yaml

# Deploy the Locust Master and Worker pods (1 Master, 3 Workers)
kubectl apply -f infrastructure/k8s/locust.yaml

# Monitor deployment progress
kubectl get pods -w
```

#### Accessing the Interfaces (Local Port-Forwarding)
```bash
# Access Locust UI (http://localhost:8089)
kubectl port-forward svc/locust-master 8089:8089

# Access Grafana Dashboard (http://localhost:3000)
kubectl port-forward svc/grafana 3000:3000
```

#### Grafana Configuration
1.  Open Grafana at `http://localhost:3000` (Default credentials: `admin` / `admin`).
2.  Add a new **Prometheus** Data Source using the internal URL: `http://prometheus:9090`.
3.  Import a Locust Dashboard using ID **`20462`** or **`11985`** to visualize requests, latency, failures, and virtual users.

#### Available Custom Prometheus Metrics
The Locust master aggregates cluster-wide performance metrics and exposes them on port `9191`:
*   `locust_users`: Active virtual user count.
*   `locust_requests_total`: Cumulative count of requests (labeled by `method`, `name`, and `status`).
*   `locust_rps`: Current cluster-wide requests per second.
*   `locust_avg_response_time_ms`: Current cluster-wide average latency in milliseconds.

---

## 🔄 CI/CD with Jenkins

The included `infrastructure/jenkins/Jenkinsfile` defines a production-grade, containerized continuous integration and deployment pipeline. It automates building isolated test/performance Docker environments, **executing the Autonomous AI QA Testing Agent to generate real-time regression tests**, running validation suites, and orchestrating rolling deployments on Kubernetes.

### 1. Jenkins Architecture & Flow
```text
[SCM Checkout]
       │
       ▼
[Build Docker Images]
       │
       ▼
[Autonomous AI QA Agent] ──(Auto-generates regression test files)
       │                                     │
       ▼                                     ▼
[Run API Tests (Containerized)] <────────────┘ (Runs all core + auto-generated tests)
       │
       ▼
[Publish HTML Report]
       │
       ▼
[Deploy to K8s]
```

### 2. Jenkins Prerequisites & Requirements

To successfully run this pipeline, ensure your Jenkins server meets the following requirements:

#### Required Jenkins Plugins
Ensure these plugins are installed and updated in your Jenkins controller (`Manage Jenkins` -> `Plugins` -> `Installed plugins`):
*   **Docker Pipeline** (and dependencies): Allows utilizing the `docker` DSL for building and registry interactions.
*   **HTML Publisher**: Required to capture and display the interactive Pytest reports directly in the Jenkins build UI.
*   **Git Plugin**: Used to pull down SCM changes.
*   **Credentials Binding Plugin**: Allows secure exposure of secret texts (like API keys) to the runner environment.

#### Build Agent Node Dependencies
The Jenkins agent (executor) executing this job must have the following system binaries and permissions:
*   **Docker Engine**: The agent user must be part of the `docker` group to run commands like `docker build` and `docker run` without root/sudo.
*   **Kubectl CLI**: Installed and configured with `~/.kube/config` pointing to the target Kubernetes cluster with sufficient privileges (to deploy and rolling-update resources).

#### Jenkins Credentials Configuration
Configure the following two credentials within Jenkins (`Manage Jenkins` -> `Credentials` -> `System` -> `Global credentials`):
1.  **Docker Registry Credentials:**
    *   **ID:** `docker-registry-credentials`
    *   **Type:** Username with password
    *   **Username:** Your Docker Hub username (e.g., `yourusername`)
    *   **Password:** Your Docker Hub Access Token (highly recommended over your password for security)
2.  **Google Gemini API Key (For the AI QA Agent):**
    *   **ID:** `gemini-api-key`
    *   **Type:** Secret text
    *   **Secret:** Your Google Gemini API Key

---

### 3. Pipeline Configuration Settings & Parameters

When you first load this pipeline, it registers as a **Parameterized Pipeline** in the Jenkins UI. When clicking **Build with Parameters**, you will be presented with the following options:

*   **`AI_QA_OBJECTIVE`**: A custom natural language prompt/objective for the AI Testing Agent. (Default: `"Verify pet inventory API and place a temporary order to see if inventory updates"`).
*   **`AI_QA_MODEL`**: The Google Gemini model to utilize. (Default: `"gemini-2.5-flash"`).
*   **`RUN_AI_QA_AGENT`**: A simple checkbox toggle to enable or disable running the AI agent during the pipeline execution. (Default: `true`).

#### Environment Variables in `Jenkinsfile`
Open `infrastructure/jenkins/Jenkinsfile` and review the `environment` block. Update the `DOCKER_HUB_USER_RAW` variable to match your own Docker Hub username:

```groovy
environment {
    // Set this to your actual Docker Hub username
    DOCKER_HUB_USER_RAW = "your-dockerhub-username"
    DOCKER_CONTEXT = 'default'
}
```

*Note: You can also override environment variables globally in Jenkins under `Manage Jenkins` -> `System` -> `Global properties` -> `Environment variables`.*

---

### 4. Detailed Stage Breakdown

#### Stage 1: SCM Checkout (`Checkout`)
*   Fetches the source code from the configured repository using SCM parameters.

#### Stage 2: Build & Push Images (`Build and Push Images`)
*   Converts the Docker username to lowercase to guarantee image naming compatibility.
*   Builds two distinct Docker images:
    *   **Pytest Runner**: `infrastructure/docker/Dockerfile.pytest`
    *   **Locust Performance Runner**: `infrastructure/docker/Dockerfile.locust`
*   Saves images under both the unique Jenkins build number (`${env.BUILD_NUMBER}`) and the `latest` tag.
*   Safely authenticates against Docker Hub via the `docker-registry-credentials` block and pushes all four tags to the registry.

#### Stage 3: Autonomous AI QA Agent (`Autonomous AI QA Agent`)
*   Runs only if `RUN_AI_QA_AGENT` is checked.
*   Binds the `gemini-api-key` Secret Text credential into the container as `GEMINI_API_KEY`.
*   Launches the CLI runner inside the newly built Docker environment:
    ```bash
    docker run --rm -v ${WORKSPACE}/tests:/app/tests -e GEMINI_API_KEY=${GEMINI_API_KEY} ${pytest_image} python agents/cli_runner.py ...
    ```
*   **Directory Volume Mount (`-v ${WORKSPACE}/tests:/app/tests`)**: By mounting the host's `tests/` directory to the container's `/app/tests/`, any new test files written by the AI Agent (such as `test_agent_*.py` files written via `write_pytest_test`) are saved directly back to your Jenkins host workspace!
*   **Error Tolerance**: If the API key is missing or the agent encounters an execution issue, the pipeline intercepts the error, marks the stage as **Unstable**, and continues to the functional validation stage instead of failing the entire build.

#### Stage 4: Automated Validation (`API Tests (Pytest)`)
*   Creates a `reports/` directory on the Jenkins executor workspace.
*   Executes the test suite inside the pytest container, mounting both `reports/` and `tests/`:
    ```bash
    docker run --rm -v ${WORKSPACE}/reports:/app/reports -v ${WORKSPACE}/tests:/app/tests ${pytest_image}
    ```
*   **Automated Regression Execution**: Because the `tests/` directory is mounted, any regression test files auto-generated by the AI Agent in the previous stage are automatically run during this block alongside the core tests!
*   **Post-execution step (Always):** Leverages the HTML Publisher plugin to parse `/reports/report.html` and publish it under the **Pytest API Report** link directly on the Jenkins Build project page.

#### Stage 5: Rolling Deployment (`Deploy Performance Infrastructure (K8s)`)
*   Deploys/applies the Locust Kubernetes specifications:
    ```bash
    kubectl apply -f infrastructure/k8s/locust.yaml
    ```
*   Executes a zero-downtime rolling update on the running Locust cluster by pointing the deployments to the newly built and pushed Locust image:
    ```bash
    kubectl set image deployment/locust-master locust-master=${env.FINAL_LOCUST_IMAGE}
    kubectl set image deployment/locust-worker locust-worker=${env.FINAL_LOCUST_IMAGE}
    ```

---

### 5. Creating the Pipeline in Jenkins UI

1.  Navigate to your Jenkins Dashboard and click **New Item**.
2.  Enter an item name (e.g., `petstore-qa-pipeline`), select **Pipeline**, and click **OK**.
3.  Scroll down to the **Pipeline** section:
    *   **Definition:** Select *Pipeline script from SCM*.
    *   **SCM:** Select *Git*.
    *   **Repository URL:** Enter your Petstore repository URL (e.g., `https://github.com/your-username/petstore.git`).
    *   **Credentials:** Select your SCM/Git credentials if your repository is private.
    *   **Branch Specifier:** Specify the branch to track (e.g., `*/main`).
    *   **Script Path:** Enter `infrastructure/jenkins/Jenkinsfile`.
4.  Click **Save**.
5.  Click **Build Now** to execute your first pipeline run! After completion, check the **Pytest API Report** sidebar link on the build dashboard to view functional verification results.
6.  For subsequent runs, use the **Build with Parameters** option to type custom natural language prompts directly to the AI testing agent.

---

## 🔍 Troubleshooting

*   **"Missing Gemini API Key" Warning:**
    If you receive an API key warning when running the QA Agent, ensure `GEMINI_API_KEY` is exported correctly in your shell or exists in a `.env` file in the directory where the command is being run.
*   **No Metrics in Grafana/Prometheus:**
    Ensure you have clicked **"Start Swarming"** in the Locust UI. Custom metrics are generated lazily upon the first actual request.
*   **Kubernetes Image Pull BackOff:**
    Verify that `DOCKER_HUB_USER_RAW` in the `Jenkinsfile` and the image paths in `locust.yaml` match your container registry namespace.
