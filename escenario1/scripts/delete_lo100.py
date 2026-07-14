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

headers = {"Content-Type": "application/yang-data+json", "Accept": "application/yang-data+json"}
base_url = f"https://{HOST}:{PORT}/restconf/data"

print("=== Paso 1: Creando Loopback100 ===")
create_payload = {
    "openconfig-interfaces:interface": [{
        "name": "Loopback100",
        "config": {
            "name": "Loopback100",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "description": "test_loopback"
        }
    }]
}
r = requests.post(f"{base_url}/openconfig-interfaces:interfaces",
                  auth=HTTPBasicAuth(USER, PASS), headers=headers,
                  data=json.dumps(create_payload), verify=False)
print(f"Create status code: {r.status_code}")

print("\n=== Paso 2: Leyendo Loopback100 ===")
r = requests.get(f"{base_url}/openconfig-interfaces:interfaces/interface=Loopback100",
                 auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)
print(f"GET status code: {r.status_code}")

print("\n=== Paso 3: Borrando Loopback100 ===")
r = requests.delete(f"{base_url}/openconfig-interfaces:interfaces/interface=Loopback100",
                    auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)
print(f"DELETE status code: {r.status_code}")

print("\n=== Paso 4: Verificando que ya no existe ===")
r = requests.get(f"{base_url}/openconfig-interfaces:interfaces/interface=Loopback100",
                 auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)
print(f"GET status code: {r.status_code} (404 = borrada correctamente)")