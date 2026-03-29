#!/bin/bash

apt update -y
apt install -y python3-pip git

git clone https://github.com/nk1044/CSL7510_assignment3.git
cd CSL7510_assignment3/api

pip3 install fastapi uvicorn psutil prometheus-client

uvicorn main:app --host 0.0.0.0 --port 8000