#!/usr/bin/env python3
"""
get_interfaces.py
Consulta el estado y configuracion de direccionamiento IP de las interfaces
de un router Arista cEOS mediante RESTCONF (OpenConfig).

Uso:
  python3 get_interfaces.py [--router r1|r2|r3] [--host <IP>]
                             [--port <PUERTO>] [--user <USUARIO>] [--password <PASSWORD>]
                             [--interface <NOMBRE>] [--only-ip]

Ejemplos:
  python3 get_interfaces.py --router r1
  python3 get_interfaces.py --router r1 --only-ip
  python3 get_interfaces.py --router r1 --interface Ethernet1
  python3 get_interfaces.py --host 172.20.20.9 --only-ip
"""

import argparse
import json
import subprocess
import sys
import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

CLAB_PREFIX   = "clab-routing-testbed"
RESTCONF_BASE = "https://{host}:{port}/restconf/data"
HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json"
}


def get_router_ip(name):
    """Obtiene la IP de gestion de un router via docker inspect."""
    try:
        result = subprocess.run(
            ["sudo", "docker", "inspect",
             f"{CLAB_PREFIX}-{name}",
             "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"],
            capture_output=True, text=True, timeout=5
        )
        ip = result.stdout.strip()
        if ip:
            return ip
        print(f"[ERROR] No se pudo obtener IP de {name}. Comprueba que el testbed esta desplegado.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error obteniendo IP de {name}: {e}")
        sys.exit(1)


def get_all_interfaces(host, port, user, password):
    url = f"{RESTCONF_BASE.format(host=host, port=port)}/openconfig-interfaces:interfaces"
    resp = requests.get(url, auth=HTTPBasicAuth(user, password),
                        headers=HEADERS, verify=False, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_single_interface(host, port, user, password, iface):
    url = (f"{RESTCONF_BASE.format(host=host, port=port)}"
           f"/openconfig-interfaces:interfaces/interface={iface}")
    resp = requests.get(url, auth=HTTPBasicAuth(user, password),
                        headers=HEADERS, verify=False, timeout=10)
    resp.raise_for_status()
    return resp.json()


def extract_ip_info(iface_data):
    results = []
    interfaces = iface_data.get("openconfig-interfaces:interfaces", {}).get("interface", [])
    if not interfaces:
        single = iface_data.get("openconfig-interfaces:interface", [])
        interfaces = single if isinstance(single, list) else [single]

    for iface in interfaces:
        name         = iface.get("name", "N/A")
        state        = iface.get("state", {})
        admin_status = state.get("admin-status", "N/A")
        oper_status  = state.get("oper-status", "N/A")

        ip_addresses = []
        for sub in iface.get("subinterfaces", {}).get("subinterface", []):
            for addr in (sub.get("openconfig-if-ip:ipv4", {})
                            .get("addresses", {}).get("address", [])):
                ip_addresses.append({
                    "version": "IPv4",
                    "address": addr.get("ip", ""),
                    "prefix":  addr.get("state", {}).get("prefix-length", "")
                })
            for addr in (sub.get("openconfig-if-ip:ipv6", {})
                            .get("addresses", {}).get("address", [])):
                ip_addresses.append({
                    "version": "IPv6",
                    "address": addr.get("ip", ""),
                    "prefix":  addr.get("state", {}).get("prefix-length", "")
                })

        results.append({
            "name": name,
            "admin_status": admin_status,
            "oper_status":  oper_status,
            "ip_addresses": ip_addresses
        })
    return results


def print_interfaces(interfaces, only_ip=False):
    for iface in interfaces:
        if only_ip and not iface["ip_addresses"]:
            continue
        print(f"\n{'='*55}")
        print(f"  Interfaz : {iface['name']}")
        print(f"  Admin    : {iface['admin_status']}")
        print(f"  Oper     : {iface['oper_status']}")
        if iface["ip_addresses"]:
            print("  Direcciones IP:")
            for addr in iface["ip_addresses"]:
                print(f"    [{addr['version']}] {addr['address']}/{addr['prefix']}")
        else:
            print("  Direcciones IP: (ninguna configurada)")
    print(f"{'='*55}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta interfaces IP de un router cEOS via RESTCONF")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--router",    choices=["r1", "r2", "r3"],
                       help="Nombre del router (detecta IP automaticamente)")
    group.add_argument("--host",      help="IP o hostname del router")
    parser.add_argument("--port",      default=5900,   type=int, help="Puerto RESTCONF (default: 5900)")
    parser.add_argument("--user",      default="admin", help="Usuario (default: admin)")
    parser.add_argument("--password",  default="admin", dest="password", help="Contrasena (default: admin)")
    parser.add_argument("--interface", default=None,   help="Nombre de interfaz especifica (ej: Ethernet1)")
    parser.add_argument("--only-ip",   action="store_true", help="Mostrar solo interfaces con IP configurada")
    parser.add_argument("--json",      action="store_true", help="Mostrar salida en formato JSON crudo")
    args = parser.parse_args()

    host = get_router_ip(args.router) if args.router else args.host

    try:
        if args.interface:
            data = get_single_interface(host, args.port, args.user, args.password, args.interface)
        else:
            data = get_all_interfaces(host, args.port, args.user, args.password)
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] No se puede conectar a {host}:{args.port}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout al conectar con {host}:{args.port}")
        sys.exit(1)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    interfaces = extract_ip_info(data)
    if not interfaces:
        print("[INFO] No se encontraron interfaces.")
        return

    print(f"\n[Router: {host}:{args.port}]  Interfaces IP")
    print_interfaces(interfaces, only_ip=args.only_ip)


if __name__ == "__main__":
    main()