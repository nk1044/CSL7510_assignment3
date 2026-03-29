# VCC Assignment 3

## Overview

This project implements a hybrid auto-scaling system where a local virtual machine is monitored for resource usage, and when CPU usage exceeds a defined threshold (75%), a new virtual machine is automatically provisioned on Google Cloud Platform (GCP).

The system demonstrates integration between monitoring tools, automation scripts, and cloud infrastructure.

---

## Tech Stack

- **FastAPI** – Application layer (metrics exposure)
- **Prometheus** – Metrics collection
- **Grafana** – Visualization dashboard
- **Python (requests, psutil)** – Autoscaler logic
- **Docker Compose** – Monitoring stack deployment
- **GCP Compute Engine** – Cloud scaling target

---

## Architecture

```

Local VM (FastAPI + Metrics)
↓
Prometheus (scrapes metrics)
↓
Grafana (visualization)
↓
Autoscaler (Python script)
↓ (CPU > 75%)
GCP VM Creation (gcloud CLI)
↓
Startup Script → Deploy App

```

---

## Folder Structure

```

hybrid-autoscale/
├── api/                  # FastAPI app
│   ├── main.py
│   ├── pyproject.toml
│   └── .python-version
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       └── dashboard.json
├── autoscaler/
│   └── autoscaler.py
├── gcp/
│   ├── startup-script.sh
│   └── deploy.sh
├── docker-compose.yml
├── .env.example
└── README.md

````

---

## Setup Instructions

### 1. Run FastAPI Application

```bash
cd api
uv venv
uv pip install -r pyproject.toml
uv run uvicorn main:app --host 0.0.0.0 --port 8000
````

Metrics endpoint:

```
http://localhost:8001
```

---

### 2. Start Monitoring Stack

```bash
docker-compose up -d
```

Access:

* Prometheus → [http://localhost:9090](http://localhost:9090)
* Grafana → [http://localhost:3000](http://localhost:3000)

---

### 3. Configure Prometheus

Update `monitoring/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "fastapi"
    static_configs:
      - targets: ["172.17.0.1:8001"]
```

Restart:

```bash
docker-compose restart prometheus
```

---

### 4. Setup Grafana Dashboard

* Login → `admin / admin`
* Add Prometheus datasource:

  ```
  http://prometheus:9090
  ```
* Import dashboard or create panels using:

  ```
  cpu_usage_percent
  memory_usage_percent
  ```

---

### 5. Configure GCP

Authenticate:

```bash
gcloud auth login
gcloud config set project <your-project-id>
```

Enable Compute Engine API if not already enabled.

---

### 6. Run Autoscaler

```bash
cd autoscaler
python autoscaler.py
```

---

## How It Works

1. FastAPI exposes system metrics using `psutil`
2. Prometheus scrapes metrics every 2 seconds
3. Grafana visualizes real-time CPU and memory usage
4. Autoscaler queries Prometheus API
5. If CPU > 75%:

   * Executes `deploy.sh`
   * Creates GCP VM
   * Startup script deploys application automatically

---

## Testing Auto-Scaling

### Generate CPU Load

```bash
sudo apt install stress -y
stress --cpu 4
```

---

### Expected Behavior

* CPU usage increases in Grafana
* Autoscaler detects threshold breach
* GCP VM is created
* Application runs on new instance

---

## Key Files

### autoscaler.py

* Queries Prometheus API
* Checks CPU threshold
* Triggers scaling

### deploy.sh

* Uses `gcloud` to create VM
* Passes startup script

### startup-script.sh

* Installs dependencies
* Deploys FastAPI app on GCP VM

---

## Sample Prometheus Query

```
cpu_usage_percent
```
