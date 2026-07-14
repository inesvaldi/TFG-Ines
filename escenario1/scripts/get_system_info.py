import requests
from requests.auth import HTTPBasicAuth
import subprocess
from datetime import datetime

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
HOST_R2 = get_container_ip("clab-telemetry-testbed-arista-ceos-lab-r2")

PORT = 5900
USER = "admin"
PASS = "admin"
headers = {"Accept": "application/yang-data+json"}

def get_system_info(host, router_name):
    print(f"=== Info del sistema: {router_name} ({host}) ===")

    # --- Hostname ---
    url_hostname = f"https://{host}:{PORT}/restconf/data/system/config"
    resp = requests.get(
        url_hostname,
        auth=HTTPBasicAuth(USER, PASS),
        headers=headers,
        verify=False
    )
    print(f"Status code      : {resp.status_code}")
    if resp.ok:
        data = resp.json()
        hostname = data.get("openconfig-system:hostname", "N/A")
        domain   = data.get("openconfig-system:domain-name", "N/A")
        print(f"Hostname         : {hostname}")
        print(f"Domain name      : {domain}")

    # --- Estado del sistema (uptime, boot time) ---
    url_state = f"https://{host}:{PORT}/restconf/data/system/state"
    resp_state = requests.get(
        url_state,
        auth=HTTPBasicAuth(USER, PASS),
        headers=headers,
        verify=False
    )
    if resp_state.ok:
        state = resp_state.json()
        boot_time = state.get("openconfig-system:boot-time", "N/A")
        current   = state.get("openconfig-system:current-datetime", "N/A")

        if boot_time != "N/A":
            boot_dt = datetime.fromtimestamp(int(boot_time) / 1e9)
            print(f"Boot time        : {boot_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"Boot time        : N/A")

        print(f"Current datetime : {current}")
    else:
        print(f"Estado del sistema no disponible (código {resp_state.status_code})")

    print()

# --- Consulta R1 y R2 ---
get_system_info(HOST_R1, "R1")
get_system_info(HOST_R2, "R2")