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

headers = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json"
}

api_call = f"https://{HOST}:{PORT}/restconf/data/openconfig-interfaces:interfaces/interface=Ethernet1/config"

result_before = requests.get(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)
print("=== Config ANTES del cambio (GET) ===")
print(json.dumps(result_before.json(), indent=2))
print()

payload = {
    "openconfig-interfaces:name": "Ethernet1",
    "openconfig-interfaces:type": "iana-if-type:ethernetCsmacd",
    "openconfig-interfaces:mtu": 0,
    "openconfig-interfaces:description": "restconf_python_test",
    "openconfig-interfaces:enabled": True
}

result_put = requests.put(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers,
                          data=json.dumps(payload), verify=False)
print(f"PUT status code: {result_put.status_code}")
print()

result_after = requests.get(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)
print("=== Config DESPUES del cambio (GET) ===")
print(json.dumps(result_after.json(), indent=2))