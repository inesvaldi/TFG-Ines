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

requests.packages.urllib3.disable_warnings()

headers = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json"
}

api_call = f"https://{HOST}:{PORT}/restconf/data/openconfig-interfaces:interfaces/interface=Ethernet1/config"

# Leer descripcion ANTES del cambio
result_before = requests.get(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)
print("=== Descripcion ANTES del cambio (GET) ===")
before_data = result_before.json()
print(f"Descripcion actual: {before_data.get('openconfig-interfaces:description')}")
print()

# Modificar solo la descripcion con POST (sin tocar el resto de campos)
payload = {
    "openconfig-interfaces:description": "modificado_con_post_python"
}

result_post = requests.post(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers,
                            data=json.dumps(payload), verify=False)
print(f"POST status code: {result_post.status_code}")
print()

# Verificar DESPUES del cambio
result_after = requests.get(api_call, auth=HTTPBasicAuth(USER, PASS), headers=headers, verify=False)
print("=== Descripcion DESPUES del cambio (GET) ===")
after_data = result_after.json()
print(f"Descripcion nueva: {after_data.get('openconfig-interfaces:description')}")