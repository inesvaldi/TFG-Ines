import requests
from requests.auth import HTTPBasicAuth
import json
import urllib3

urllib3.disable_warnings()

USER = 'admin'
PASS = 'admin'
HEADERS = {
    'Content-Type': 'application/yang-data+json',
    'Accept': 'application/yang-data+json'
}

def restconf_post(host, path, payload):
    url = f"https://{host}:5900/restconf/data/{path}"
    response = requests.post(url, auth=HTTPBasicAuth(USER, PASS),
                             headers=HEADERS, data=json.dumps(payload), verify=False)
    print(f"POST {url} -> {response.status_code}")
    if response.status_code not in (200, 201, 204):
        print(f"  ERROR: {response.text}")
    return response

def configure_interface_ip(host, iface, ip, prefix_len):
    path = f"openconfig-interfaces:interfaces/interface={iface}/subinterfaces/subinterface=0/openconfig-if-ip:ipv4/addresses"
    payload = {
        "openconfig-if-ip:address": [
            {
                "ip": ip,
                "config": {
                    "ip": ip,
                    "prefix-length": prefix_len
                }
            }
        ]
    }
    return restconf_post(host, path, payload)

def configure_static_routes(host, routes):
    path = "openconfig-network-instance:network-instances/network-instance=default/protocols"
    static_list = []
    for i, (prefix, prefix_len, next_hop) in enumerate(routes):
        static_list.append({
            "prefix": f"{prefix}/{prefix_len}",
            "config": {
                "prefix": f"{prefix}/{prefix_len}"
            },
            "next-hops": {
                "next-hop": [
                    {
                        "index": str(i + 1),
                        "config": {
                            "index": str(i + 1),
                            "next-hop": next_hop,
                            "metric": 0
                        }
                    }
                ]
            }
        })
    payload = {
        "openconfig-network-instance:protocol": [
            {
                "identifier": "STATIC",
                "name": "STATIC",
                "config": {
                    "identifier": "STATIC",
                    "name": "STATIC",
                    "enabled": True
                },
                "static-routes": {
                    "static": static_list
                }
            }
        ]
    }
    return restconf_post(host, path, payload)

routers = {
    "clab-routing-testbed-r1": {
        "interfaces": [
            ("Ethernet1", "192.168.1.1", 24),
            ("Ethernet2", "10.10.10.1", 30),
            ("Ethernet3", "10.10.11.1", 30),
        ],
        "static_routes": [
            ("192.168.2.0", 24, "10.10.10.2"),
            ("192.168.3.0", 24, "10.10.11.2"),
        ]
    },
    "clab-routing-testbed-r2": {
        "interfaces": [
            ("Ethernet1", "192.168.2.1", 24),
            ("Ethernet2", "10.10.10.2", 30),
            ("Ethernet3", "10.10.12.1", 30),
        ],
        "static_routes": [
            ("192.168.1.0", 24, "10.10.10.1"),
            ("192.168.3.0", 24, "10.10.12.2"),
        ]
    },
    "clab-routing-testbed-r3": {
        "interfaces": [
            ("Ethernet1", "192.168.3.1", 24),
            ("Ethernet2", "10.10.11.2", 30),
            ("Ethernet3", "10.10.12.2", 30),
        ],
        "static_routes": [
            ("192.168.1.0", 24, "10.10.11.1"),
            ("192.168.2.0", 24, "10.10.12.1"),
        ]
    }
}

for router, config in routers.items():
    print(f"\n{'='*60}")
    print(f"Configurando {router}...")
    print(f"{'='*60}")

    print("\n--- Interfaces IP ---")
    for iface, ip, prefix_len in config["interfaces"]:
        configure_interface_ip(router, iface, ip, prefix_len)

    print("\n--- Rutas estaticas ---")
    configure_static_routes(router, config["static_routes"])

print("\n Configuracion completada.")