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

HOST_R1 = get_container_ip("clab-telemetry-testbed-arista-ceos-lab-r1")

PORT = 5900
USER = "admin"
PASS = "admin"

headers = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json"
}

NEW_MTU = 9000  # Cambia este valor según lo que quieras probar

NEW_DESCRIPTION = "Enlace R1-R2 modificado con PATCH"

# --- Consulta descripción antes del cambio ---
url_state = (
    f"https://{HOST_R1}:{PORT}/restconf/data/"
    f"openconfig-interfaces:interfaces/interface=Ethernet1/state"
)
resp_before = requests.get(
    url_state,
    auth=HTTPBasicAuth(USER, PASS),
    headers=headers,
    verify=False
)
desc_before = resp_before.json().get("openconfig-interfaces:description", "N/A")
print(f"Descripción antes del PATCH : {desc_before}")

# --- PATCH: modifica solo la descripción ---
url_patch = (
    f"https://{HOST_R1}:{PORT}/restconf/data/"
    f"openconfig-interfaces:interfaces/interface=Ethernet1/config"
)
payload = {
    "name":        "Ethernet1",
    "description": NEW_DESCRIPTION,
    "enabled":     True
}
resp_patch = requests.patch(
    url_patch,
    auth=HTTPBasicAuth(USER, PASS),
    headers=headers,
    json=payload,
    verify=False
)
print(f"Status code PATCH           : {resp_patch.status_code}")
print(f"OK                          : {resp_patch.ok}")

# --- Consulta descripción después del cambio ---
resp_after = requests.get(
    url_state,
    auth=HTTPBasicAuth(USER, PASS),
    headers=headers,
    verify=False
)
desc_after = resp_after.json().get("openconfig-interfaces:description", "N/A")
print(f"Descripción después del PATCH: {desc_after}")