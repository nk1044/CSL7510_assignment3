from fastapi import FastAPI
import psutil
from prometheus_client import start_http_server, Gauge
import threading
import time

app = FastAPI()

cpu_usage = Gauge('cpu_usage_percent', 'CPU usage in percent')
memory_usage = Gauge('memory_usage_percent', 'Memory usage in percent')

def collect_metrics():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent

        cpu_usage.set(cpu)
        memory_usage.set(mem)

        time.sleep(2)

@app.get("/")
def root():
    return {"message": "Hybrid AutoScale App Running"}

def start_metrics():
    start_http_server(8001)
    threading.Thread(target=collect_metrics).start()

start_metrics()