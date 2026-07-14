import requests
from requests.auth import HTTPBasicAuth
import subprocess
import json

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

result = requests.get(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)

print(f"Status code: {result.status_code}")
print(f"OK: {result.ok}")
print()

data = result.json()

print("=== Estado de Ethernet1 (r1) ===")
print(f"Admin status : {data.get('openconfig-interfaces:admin-status')}")
print(f"Oper status  : {data.get('openconfig-interfaces:oper-status')}")
print(f"Descripcion  : {data.get('openconfig-interfaces:description')}")
print(f"MTU          : {data.get('openconfig-interfaces:mtu')}")
print()

counters = data.get("openconfig-interfaces:counters", {})
print("=== Contadores ===")
print(f"in-octets        : {counters.get('in-octets')}")
print(f"out-octets       : {counters.get('out-octets')}")
print(f"in-unicast-pkts  : {counters.get('in-unicast-pkts')}")
print(f"out-unicast-pkts : {counters.get('out-unicast-pkts')}")
print(f"in-errors        : {counters.get('in-errors')}")
print(f"out-errors       : {counters.get('out-errors')}")