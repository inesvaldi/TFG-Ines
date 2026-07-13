#!/usr/bin/env python3
"""
get_routing_table.py
Consulta la tabla de encaminamiento IP de un router Arista cEOS
mediante RESTCONF (OpenConfig network-instance / local-static routes).

Uso:
  python3 get_routing_table.py [--router r1|r2|r3] [--host <IP>]
                                [--port <PUERTO>] [--user <USUARIO>] [--password <PASSWORD>]
                                [--vrf <VRF>] [--protocol <PROTOCOLO>]

Ejemplos:
  python3 get_routing_table.py --router r1
  python3 get_routing_table.py --router r1 --protocol static
  python3 get_routing_table.py --router r1 --protocol rib
  python3 get_routing_table.py --host 172.20.20.9 --protocol static
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

ROUTES_URL = ("{base}/openconfig-network-instance:network-instances"
              "/network-instance={vrf}/afts")
STATIC_URL = ("{base}/openconfig-network-instance:network-instances"
              "/network-instance={vrf}/protocols"
              "/protocol=STATIC,STATIC/static-routes")


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


def get_rib(host, port, user, password, vrf):
    url = ROUTES_URL.format(base=RESTCONF_BASE.format(host=host, port=port), vrf=vrf)
    resp = requests.get(url, auth=HTTPBasicAuth(user, password),
                        headers=HEADERS, verify=False, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_static_routes(host, port, user, password, vrf):
    url = STATIC_URL.format(base=RESTCONF_BASE.format(host=host, port=port), vrf=vrf)
    resp = requests.get(url, auth=HTTPBasicAuth(user, password),
                        headers=HEADERS, verify=False, timeout=10)
    resp.raise_for_status()
    return resp.json()


def parse_rib(data):
    routes = []
    afts = data.get("openconfig-network-instance:afts", {})
    fib_entries = (afts.get("ipv4-unicast", {})
                       .get("fib-entries", {})
                       .get("fib-entry", []))
    for entry in fib_entries:
        prefix = entry.get("ip-prefix", "N/A")
        origin = entry.get("state", {}).get("origin-protocol", "N/A")
        next_hops = []
        for nh in entry.get("next-hops", {}).get("next-hop", []):
            nh_state  = nh.get("state", {})
            gw        = nh_state.get("ip-address", "")
            idx       = nh_state.get("index", "")
            iface_ref = nh.get("interface-ref", {}).get("state", {}).get("interface", "")
            next_hops.append({"gateway": gw or idx, "interface": iface_ref})
        routes.append({"prefix": prefix, "protocol": origin, "next_hops": next_hops})
    return routes


def parse_static_routes(data):
    routes = []
    static_routes = data.get("openconfig-network-instance:static", [])
    for rt in static_routes:
        prefix = rt.get("prefix", "N/A")
        next_hops = []
        for nh in rt.get("next-hops", {}).get("next-hop", []):
            nh_cfg = nh.get("config", {})
            gw     = nh_cfg.get("next-hop", "N/A")
            metric = nh_cfg.get("metric", "N/A")
            next_hops.append({"gateway": gw, "metric": metric})
        routes.append({"prefix": prefix, "protocol": "STATIC (config)", "next_hops": next_hops})
    return routes


def print_routes(routes, title="Tabla de encaminamiento"):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")
    if not routes:
        print("  (sin rutas encontradas)")
    for rt in routes:
        print(f"\n  Prefijo  : {rt['prefix']}")
        print(f"  Protocolo: {rt['protocol']}")
        if rt["next_hops"]:
            for nh in rt["next_hops"]:
                gw_info = f"via {nh.get('gateway','')}"
                if nh.get("interface"):
                    gw_info += f"  dev {nh['interface']}"
                if nh.get("metric") not in (None, "N/A", ""):
                    gw_info += f"  metric {nh['metric']}"
                print(f"  Next-hop : {gw_info}")
        else:
            print("  Next-hop : (directo / sin next-hop)")
    print(f"\n{'='*65}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta tabla de encaminamiento de un router cEOS via RESTCONF")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--router",    choices=["r1", "r2", "r3"],
                       help="Nombre del router (detecta IP automaticamente)")
    group.add_argument("--host",      help="IP o hostname del router")
    parser.add_argument("--port",      default=5900,     type=int, help="Puerto RESTCONF (default: 5900)")
    parser.add_argument("--user",      default="admin",  help="Usuario (default: admin)")
    parser.add_argument("--password",  default="admin",  dest="password", help="Contrasena (default: admin)")
    parser.add_argument("--vrf",       default="default", help="VRF a consultar (default: default)")
    parser.add_argument("--protocol",  default="all",
                        choices=["all", "static", "rib"],
                        help="Fuente a consultar: all | static | rib (default: all)")
    parser.add_argument("--json",      action="store_true", help="Mostrar salida en formato JSON crudo")
    args = parser.parse_args()

    host = get_router_ip(args.router) if args.router else args.host

    routes = []

    try:
        if args.protocol in ("all", "static"):
            try:
                data = get_static_routes(host, args.port, args.user, args.password, args.vrf)
                if args.json:
                    print(json.dumps(data, indent=2))
                    return
                routes += parse_static_routes(data)
            except requests.exceptions.HTTPError as e:
                print(f"[WARN] Rutas estaticas no disponibles: HTTP {e.response.status_code}")

        if args.protocol in ("all", "rib"):
            try:
                data = get_rib(host, args.port, args.user, args.password, args.vrf)
                if args.json:
                    print(json.dumps(data, indent=2))
                    return
                routes += parse_rib(data)
            except requests.exceptions.HTTPError as e:
                print(f"[WARN] RIB no disponible: HTTP {e.response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] No se puede conectar a {host}:{args.port}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout al conectar con {host}:{args.port}")
        sys.exit(1)

    print(f"\n[Router: {host}:{args.port}]  VRF: {args.vrf}")
    print_routes(routes, title=f"Tabla de encaminamiento  [{args.protocol.upper()}]")


if __name__ == "__main__":
    main()