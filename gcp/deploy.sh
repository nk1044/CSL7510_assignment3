#!/bin/bash

INSTANCE_NAME=autoscale-vm

gcloud compute instances create $INSTANCE_NAME \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --metadata-from-file startup-script=startup-script.sh