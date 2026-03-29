import requests
import time
import os

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
THRESHOLD = 75

def get_cpu():
    query = 'cpu_usage_percent'
    r = requests.get(PROMETHEUS_URL, params={'query': query})
    data = r.json()

    try:
        return float(data['data']['result'][0]['value'][1])
    except:
        return 0

def trigger_gcp():
    print("Threshold exceeded. Triggering GCP VM...")
    os.system("bash ../gcp/deploy.sh")

def main():
    while True:
        cpu = get_cpu()
        print(f"CPU: {cpu}")

        if cpu > THRESHOLD:
            trigger_gcp()
            break

        time.sleep(5)

if __name__ == "__main__":
    main()