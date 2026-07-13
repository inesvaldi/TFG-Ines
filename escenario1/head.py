import requests
from requests.auth import HTTPBasicAuth
import subprocess

requests.packages.urllib3.disable_warnings()

# --- IP dinámica ---
def get_container_ip(container_name):
    result = subprocess.run(
        ["sudo", "docker", "inspect", container_name,
         "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"],
        capture_output=True, text=True
    )
    return result.stdout.strip()

HOST = get_container_ip("clab-telemetry-testbed-arista-ceos-lab-r1")

PORT = 5900
USER = "admin"
PASS = "admin"

headers = {"Accept": "application/yang-data+json"}

api_call = f"https://{HOST}:{PORT}/restconf/data/openconfig-interfaces:interfaces/interface=Ethernet1/state"

result = requests.head(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)

print(f"URL         : {result.url}")
print(f"Status code : {result.status_code}")
print(f"Headers     : {dict(result.headers)}")
print(f"Content     : {result.content}")