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

    # fetch external IP
    result = subprocess.run(
        ["gcloud", "compute", "instances", "describe", "autoscaled-vm",
         "--format=get(networkInterfaces[0].accessConfigs[0].natIP)"],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()