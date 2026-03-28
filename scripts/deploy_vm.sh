#!/bin/bash

echo "Installing Python on VM..."
sudo apt update
sudo apt install python3 -y

echo "Starting app..."
python3 app.py