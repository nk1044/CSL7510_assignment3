# Cloud Auto-Scaling System with Python, Docker, and GCP

## Overview

This project implements a cloud-based auto-scaling system using Python, Docker, Nginx, and Google Cloud Platform (GCP). The system monitors CPU and memory usage of a running application. When resource usage crosses a defined threshold, it automatically provisions a new virtual machine on GCP to handle the increased load. The entire setup is containerized using Docker and orchestrated with Docker Compose.

The project is divided into four independently functioning services: the application server, the load balancer, the resource monitor, and the auto-scaler. Each service runs in its own Docker container and communicates with the others over Docker's internal network.

---

## Features

- Python-based HTTP application server (no external frameworks)
- Nginx reverse proxy acting as a load balancer
- Real-time CPU and memory monitoring using psutil
- Automatic VM provisioning on GCP via gcloud CLI when thresholds are exceeded
- Fully containerized using Docker and Docker Compose
- Modular project structure with clear separation of concerns

---

## Folder Structure

```
cloud-autoscale-python/
│
├── api/                     # Python application server
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── nginx/                   # Nginx load balancer
│   ├── nginx.conf
│   └── Dockerfile
│
├── monitoring/              # Resource usage monitor
│   ├── monitor.py
│   └── requirements.txt
│
├── scaler/                  # Auto-scaling logic
│   ├── scaler.py
│   └── gcp_utils.py
│
├── scripts/                 # VM deployment scripts
│   ├── deploy_vm.sh
│   └── setup_vm.sh
│
├── docker-compose.yml       # Service orchestration
├── .env                     # Environment variables
├── README.md
└── requirements.txt
```

---

## File Descriptions and Content

### `api/app.py`

This is the core Python HTTP server. It listens on port 5000 and returns the hostname of the container in its response. This makes it easy to verify which instance handled a given request, which is useful when multiple instances are running.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = socket.gethostname()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(f"Response from {hostname}".encode())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 5000), Handler)
    print("App running on port 5000")
    server.serve_forever()
```

### `api/Dockerfile`

Builds a minimal Python 3.9 container image and runs the application.

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

### `nginx/nginx.conf`

Configures Nginx as a reverse proxy. Incoming HTTP requests on port 80 are forwarded to the `api` service running on port 5000. The `upstream` block can be extended later to include additional backend servers as GCP VMs are provisioned.

```nginx
events {}

http {
    upstream backend {
        server api:5000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

### `nginx/Dockerfile`

Builds the Nginx image and injects the custom configuration.

```dockerfile
FROM nginx:latest
COPY nginx.conf /etc/nginx/nginx.conf
```

### `monitoring/monitor.py`

Polls CPU and memory usage every 5 seconds using the `psutil` library. If either metric exceeds 75%, it sends a POST request to the scaler service at `http://scaler:6000/scale` to trigger auto-scaling.

```python
import psutil
import time
import requests

THRESHOLD = 75

while True:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent

    print(f"CPU: {cpu}%, MEM: {mem}%")

    if cpu > THRESHOLD or mem > THRESHOLD:
        try:
            requests.post("http://scaler:6000/scale")
        except:
            pass

    time.sleep(5)
```

### `monitoring/requirements.txt`

```
psutil
requests
```

### `scaler/scaler.py`

A lightweight HTTP server listening on port 6000. When it receives a POST request at `/scale`, it calls the `create_vm()` function to provision a new GCP virtual machine and prints the resulting external IP address.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
from gcp_utils import create_vm

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/scale":
            print("Scaling triggered")
            ip = create_vm()
            print(f"New VM IP: {ip}")
            self.send_response(200)
            self.end_headers()

server = HTTPServer(("0.0.0.0", 6000), Handler)
print("Scaler running on port 6000")
server.serve_forever()
```

### `scaler/gcp_utils.py`

Contains the GCP integration logic. Uses the `gcloud` CLI to create a new VM instance and then fetches its external IP address. The VM configuration (zone, machine type, image) is defined here and should match the values in `.env`.

```python
import subprocess

def create_vm():
    cmd = [
        "gcloud", "compute", "instances", "create", "autoscaled-vm",
        "--zone=us-central1-a",
        "--machine-type=e2-medium",
        "--image-family=windows-2022",
        "--image-project=windows-cloud"
    ]

    subprocess.run(cmd)

    result = subprocess.run(
        ["gcloud", "compute", "instances", "describe", "autoscaled-vm",
         "--format=get(networkInterfaces[0].accessConfigs[0].natIP)"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()
```

### `scripts/deploy_vm.sh`

A shell script intended to be run on a newly provisioned GCP VM. It installs Python and starts the application server.

```bash
#!/bin/bash

echo "Installing Python on VM..."
sudo apt update
sudo apt install python3 -y

echo "Starting app..."
python3 app.py
```

### `docker-compose.yml`

Defines and connects all four services. The monitoring service depends on the scaler, and the Nginx service depends on the API service. All services communicate over Docker's default bridge network.

```yaml
version: '3'

services:
  api:
    build: ./api
    container_name: api
    ports:
      - "5000:5000"

  nginx:
    build: ./nginx
    container_name: nginx
    ports:
      - "80:80"
    depends_on:
      - api

  monitoring:
    build:
      context: ./monitoring
      dockerfile: ../api/Dockerfile
    container_name: monitoring
    depends_on:
      - scaler

  scaler:
    build:
      context: ./scaler
      dockerfile: ../api/Dockerfile
    container_name: scaler
    ports:
      - "6000:6000"
```

### `.env`

Stores GCP configuration values used by the scaler and gcloud commands. Replace the placeholder values with your actual GCP project details before running.

```
PROJECT_ID=your_project_id
ZONE=us-central1-a
VM_NAME=autoscaled-vm
MACHINE_TYPE=e2-medium
IMAGE_FAMILY=windows-2022
IMAGE_PROJECT=windows-cloud
```

---

## How Auto-Scaling Works

The auto-scaling mechanism follows a simple event-driven flow:

1. The `api` service starts and serves HTTP requests on port 5000.
2. Nginx listens on port 80 and forwards all traffic to the `api` container.
3. The `monitoring` service continuously checks the CPU and memory of the host machine every 5 seconds.
4. If CPU or memory usage exceeds 75%, the monitor sends a POST request to the `scaler` service at `http://scaler:6000/scale`.
5. The `scaler` receives the request, calls `gcp_utils.create_vm()`, and runs the `gcloud compute instances create` command to launch a new VM on GCP.
6. Once the VM is created, its external IP is retrieved and printed to the console. This IP can then be added to the Nginx upstream configuration to distribute traffic to the new instance.

This system demonstrates a basic reactive scaling pattern: measure load, detect threshold breach, and provision additional capacity.

---

## Prerequisites

Before running the project, ensure the following are installed and configured on your machine:

- Docker and Docker Compose
- Google Cloud SDK (`gcloud` CLI), authenticated with a valid GCP project
- Python 3.9 or higher (if running outside Docker)
- A GCP project with Compute Engine API enabled and billing active

---

## Setup Instructions

### Step 1: Clone or set up the project directory

Create the folder structure as shown above and place each file in its correct location.

### Step 2: Configure environment variables

Open the `.env` file and replace `your_project_id` with your actual GCP project ID. Adjust zone, machine type, and image values if required.

### Step 3: Authenticate with GCP

```bash
gcloud auth login
gcloud config set project your_project_id
```

### Step 4: Build and start all services

Run the following command from the root of the project directory:

```bash
docker-compose up --build
```

This will build all Docker images and start the api, nginx, monitoring, and scaler containers.

### Step 5: Verify the services are running

Open a browser or use curl to test the application:

```bash
curl http://localhost/
```

You should receive a response like:

```
Response from <container_hostname>
```

To check that the scaler is running:

```bash
curl -X POST http://localhost:6000/scale
```

This manually triggers the scaling logic and will attempt to create a VM on GCP.

### Step 6: Monitor logs

To watch what the monitoring and scaler services are doing in real time:

```bash
docker-compose logs -f monitoring
docker-compose logs -f scaler
```

---

## Demo Steps

1. Start all services with `docker-compose up --build`.
2. Open `http://localhost/` in a browser. Confirm the API responds.
3. Simulate high CPU load on the host (e.g., using a stress tool) to trigger the monitoring threshold.
4. Watch the monitoring container logs. When CPU exceeds 75%, it will POST to the scaler.
5. Observe the scaler logs. A new GCP VM will be created and its IP will be printed.
6. Optionally, add the new VM's IP to `nginx.conf` under the `upstream` block and reload Nginx to route traffic to it.

---

## Key Design Decisions

- **No Flask or external web frameworks**: Both the API server and the scaler use Python's built-in `http.server` module. This keeps the containers lightweight and reduces dependencies.
- **Service isolation**: Each concern (serving, load balancing, monitoring, scaling) is handled by a separate container. This makes the system easier to understand, debug, and extend.
- **Threshold-based scaling**: The monitor uses a fixed 75% threshold. This is intentionally simple for demonstration purposes and can be replaced with a moving average or time-based logic in a production system.
- **gcloud CLI for GCP**: Rather than using the GCP Python client library, the scaler uses subprocess calls to the `gcloud` CLI. This makes the GCP interaction visible and straightforward to test manually.
