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